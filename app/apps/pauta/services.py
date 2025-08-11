import requests
import json
import time
from datetime import datetime
from typing import Dict, Optional, Tuple
from django.utils import timezone
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class APISyncService:
    """
    Serviço para sincronização de dados das APIs do Senado Federal e Câmara dos Deputados.
    """
    
    # URLs das APIs
    SENADO_BASE_URL = "https://legis.senado.leg.br/dadosabertos"
    CAMARA_BASE_URL = "https://dadosabertos.camara.leg.br/api/v2"
    
    # Headers padrão
    DEFAULT_HEADERS = {
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    # Rate limiting
    SENADO_RATE_LIMIT = 10  # requisições por segundo
    CAMARA_RATE_LIMIT = 15  # requisições por segundo
    
    def __init__(self):
        self.last_senado_request = 0
        self.last_camara_request = 0
    
    def _rate_limit_senado(self):
        """Aplica rate limiting para a API do Senado"""
        current_time = time.time()
        time_since_last = current_time - self.last_senado_request
        if time_since_last < (1.0 / self.SENADO_RATE_LIMIT):
            sleep_time = (1.0 / self.SENADO_RATE_LIMIT) - time_since_last
            time.sleep(sleep_time)
        self.last_senado_request = time.time()
    
    def _rate_limit_camara(self):
        """Aplica rate limiting para a API da Câmara"""
        current_time = time.time()
        time_since_last = current_time - self.last_camara_request
        if time_since_last < (1.0 / self.CAMARA_RATE_LIMIT):
            sleep_time = (1.0 / self.CAMARA_RATE_LIMIT) - time_since_last
            time.sleep(sleep_time)
        self.last_camara_request = time.time()
    
    def buscar_proposicao_senado(self, tipo: str, numero: int, ano: int) -> Optional[Dict]:
        """
        Busca uma proposição na API do Senado Federal.
        
        Args:
            tipo: Tipo da proposição (PL, PEC, etc.)
            numero: Número da proposição
            ano: Ano da proposição
            
        Returns:
            Dict com os dados da proposição ou None se não encontrada
        """
        self._rate_limit_senado()
        
        # Buscar na API do Senado usando o endpoint de processo
        # A API do Senado retorna uma lista de processos, precisamos filtrar
        search_url = f"{self.SENADO_BASE_URL}/processo"
        
        try:
            response = requests.get(
                search_url, 
                headers=self.DEFAULT_HEADERS, 
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                # Processar resposta para encontrar a proposição específica
                return self._processar_resposta_senado(data, tipo, numero, ano)
            else:
                logger.warning(f"Erro ao buscar proposição no Senado: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição para API do Senado: {e}")
            return None
    
    def buscar_proposicao_camara(self, tipo: str, numero: int, ano: int) -> Optional[Dict]:
        """
        Busca uma proposição na API da Câmara dos Deputados.
        
        Args:
            tipo: Tipo da proposição (PL, PEC, etc.)
            numero: Número da proposição
            ano: Ano da proposição
            
        Returns:
            Dict com os dados da proposição ou None se não encontrada
        """
        self._rate_limit_camara()
        
        # Buscar proposição por tipo, número e ano
        search_url = f"{self.CAMARA_BASE_URL}/proposicoes"
        
        params = {
            'siglaTipo': tipo,
            'numero': numero,
            'ano': ano
        }
        
        try:
            response = requests.get(
                search_url, 
                params=params, 
                headers=self.DEFAULT_HEADERS, 
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return self._processar_resposta_camara(data, tipo, numero, ano)
            else:
                logger.warning(f"Erro ao buscar proposição na Câmara: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição para API da Câmara: {e}")
            return None
    
    def _processar_resposta_senado(self, data: Dict, tipo: str, numero: int, ano: int) -> Optional[Dict]:
        """
        Processa a resposta da API do Senado e extrai os dados necessários.
        """
        try:
            # A API do Senado retorna uma lista de processos
            if isinstance(data, list):
                # Procurar pela proposição específica baseada no tipo, número e ano
                for processo in data:
                    identificacao = processo.get('identificacao', '')
                    
                    # Verificar se a identificação contém o tipo, número e ano
                    if (tipo in identificacao and 
                        str(numero) in identificacao and 
                        str(ano) in identificacao):
                        
                        return {
                            'sf_id': processo.get('id'),
                            'autor': processo.get('autoria'),
                            'data_apresentacao': processo.get('dataApresentacao'),
                            'casa_inicial': 'SF'
                        }
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao processar resposta do Senado: {e}")
            return None
    
    def _processar_resposta_camara(self, data: Dict, tipo: str, numero: int, ano: int) -> Optional[Dict]:
        """
        Processa a resposta da API da Câmara e extrai os dados necessários.
        """
        try:
            if 'dados' in data and isinstance(data['dados'], list) and len(data['dados']) > 0:
                proposicao = data['dados'][0]
                
                # Buscar autores separadamente
                autores = self._buscar_autores_camara(proposicao.get('id'))
                
                return {
                    'cd_id': proposicao.get('id'),
                    'autor': autores[0] if autores else None,
                    'data_apresentacao': proposicao.get('dataApresentacao'),
                    'casa_inicial': 'CD'
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao processar resposta da Câmara: {e}")
            return None
    
    def _extrair_autor_senado(self, autoria: Dict) -> Optional[str]:
        """
        Extrai o nome do autor da estrutura de autoria do Senado.
        """
        try:
            if 'Autor' in autoria:
                autor = autoria['Autor']
                return autor.get('NomeParlamentar') or autor.get('Nome')
            elif 'Autores' in autoria and isinstance(autoria['Autores'], list):
                if len(autoria['Autores']) > 0:
                    autor = autoria['Autores'][0]
                    return autor.get('NomeParlamentar') or autor.get('Nome')
            return None
        except Exception:
            return None
    
    def _buscar_autores_camara(self, proposicao_id: int) -> list:
        """
        Busca os autores de uma proposição na Câmara.
        """
        if not proposicao_id:
            return []
        
        self._rate_limit_camara()
        
        url = f"{self.CAMARA_BASE_URL}/proposicoes/{proposicao_id}/autores"
        
        try:
            response = requests.get(url, headers=self.DEFAULT_HEADERS, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if 'dados' in data and isinstance(data['dados'], list):
                    return [autor.get('nome') for autor in data['dados'] if autor.get('nome')]
            
            return []
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao buscar autores na Câmara: {e}")
            return []
    
    def sincronizar_proposicao(self, proposicao) -> bool:
        """
        Sincroniza uma proposição específica com as APIs.
        
        Args:
            proposicao: Instância do modelo Proposicao
            
        Returns:
            bool: True se a sincronização foi bem-sucedida, False caso contrário
        """
        try:
            logger.info(f"Sincronizando proposição: {proposicao.identificador_completo}")
            
            # Buscar em ambas as APIs
            dados_senado = self.buscar_proposicao_senado(
                proposicao.tipo, proposicao.numero, proposicao.ano
            )
            
            dados_camara = self.buscar_proposicao_camara(
                proposicao.tipo, proposicao.numero, proposicao.ano
            )
            
            # Atualizar campos da proposição
            if dados_senado:
                proposicao.sf_id = dados_senado.get('sf_id')
                if not proposicao.autor and dados_senado.get('autor'):
                    proposicao.autor = dados_senado.get('autor')
                if not proposicao.data_apresentacao and dados_senado.get('data_apresentacao'):
                    proposicao.data_apresentacao = dados_senado.get('data_apresentacao')
                if not proposicao.casa_inicial and dados_senado.get('casa_inicial'):
                    proposicao.casa_inicial = dados_senado.get('casa_inicial')
            
            if dados_camara:
                proposicao.cd_id = dados_camara.get('cd_id')
                if not proposicao.autor and dados_camara.get('autor'):
                    proposicao.autor = dados_camara.get('autor')
                if not proposicao.data_apresentacao and dados_camara.get('data_apresentacao'):
                    proposicao.data_apresentacao = dados_camara.get('data_apresentacao')
                if not proposicao.casa_inicial and dados_camara.get('casa_inicial'):
                    proposicao.casa_inicial = dados_camara.get('casa_inicial')
            
            # Marcar como sincronizada
            proposicao.ultima_sincronizacao = timezone.now()
            proposicao.erro_sincronizacao = None
            proposicao.save()
            
            logger.info(f"Proposição {proposicao.identificador_completo} sincronizada com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao sincronizar proposição {proposicao.identificador_completo}: {e}")
            proposicao.erro_sincronizacao = str(e)
            proposicao.save()
            return False
    
    def sincronizar_todas_proposicoes(self, limit: Optional[int] = None) -> Dict[str, int]:
        """
        Sincroniza todas as proposições que precisam de sincronização.
        
        Args:
            limit: Limite de proposições a processar (None para todas)
            
        Returns:
            Dict com estatísticas da sincronização
        """
        from .models import Proposicao
        
        proposicoes = Proposicao.objects.filter(
            ultima_sincronizacao__isnull=True
        ).order_by('created_at')
        
        if limit:
            proposicoes = proposicoes[:limit]
        
        total = proposicoes.count()
        sucessos = 0
        erros = 0
        
        logger.info(f"Iniciando sincronização de {total} proposições")
        
        for proposicao in proposicoes:
            if self.sincronizar_proposicao(proposicao):
                sucessos += 1
            else:
                erros += 1
            
            # Pausa entre proposições para evitar sobrecarga
            time.sleep(0.5)
        
        logger.info(f"Sincronização concluída: {sucessos} sucessos, {erros} erros")
        
        return {
            'total': total,
            'sucessos': sucessos,
            'erros': erros
        }
