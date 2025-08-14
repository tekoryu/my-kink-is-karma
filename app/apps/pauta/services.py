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
                        
                        # Extrair casa iniciadora
                        casa_iniciadora = processo.get('siglaCasaIniciadora')
                        
                        # Extrair autor da estrutura complexa
                        autor = self._extrair_autor_senado(processo.get('autoria', {}))
                        
                        # Processar data de apresentação
                        data_apresentacao = self._processar_data(processo.get('dataApresentacao'))
                        
                        return {
                            'sf_id': processo.get('id'),
                            'autor': autor,
                            'data_apresentacao': data_apresentacao,
                            'casa_inicial': casa_iniciadora
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
                
                # Processar data de apresentação
                data_apresentacao = self._processar_data(proposicao.get('dataApresentacao'))
                
                # Determinar casa inicial baseado no autor
                casa_inicial = self._determinar_casa_inicial_camara(autores, proposicao)
                
                return {
                    'cd_id': proposicao.get('id'),
                    'autor': autores[0] if autores else None,
                    'data_apresentacao': data_apresentacao,
                    'casa_inicial': casa_inicial
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao processar resposta da Câmara: {e}")
            return None
    
    def _determinar_casa_inicial(self, dados_senado: Optional[Dict], dados_camara: Optional[Dict]) -> Optional[str]:
        """
        Determina a casa inicial baseado nos dados das APIs.
        
        Args:
            dados_senado: Dados da API do Senado
            dados_camara: Dados da API da Câmara
            
        Returns:
            str: Casa inicial determinada ou None se não conseguir determinar
        """
        # Priorizar dados do Senado se disponível
        if dados_senado and dados_senado.get('casa_inicial'):
            return dados_senado.get('casa_inicial')
        
        # Usar dados da Câmara se disponível
        if dados_camara and dados_camara.get('casa_inicial'):
            return dados_camara.get('casa_inicial')
        
        # Se apenas uma API retornou dados, usar ela como referência
        if dados_senado and not dados_camara:
            return 'SF'
        elif dados_camara and not dados_senado:
            return 'CD'
        
        # Se ambas retornaram dados mas sem casa_inicial, não conseguir determinar
        return None
    
    def _determinar_casa_inicial_camara(self, autores: list, proposicao: Dict) -> str:
        """
        Determina a casa inicial baseado nos autores da proposição na Câmara.
        
        Args:
            autores: Lista de autores da proposição
            proposicao: Dados da proposição
            
        Returns:
            str: Casa inicial determinada
        """
        if not autores:
            return 'CD'  # Default para Câmara se não conseguir determinar
        
        # Verificar se é Poder Executivo
        for autor in autores:
            if any(keyword in autor.lower() for keyword in ['executivo', 'presidente', 'ministro']):
                return 'EXECUTIVO'
        
        # Verificar se é Senado
        for autor in autores:
            if any(keyword in autor.lower() for keyword in ['senador', 'senado']):
                return 'SF'
        
        # Verificar se é Câmara
        for autor in autores:
            if any(keyword in autor.lower() for keyword in ['deputado', 'câmara']):
                return 'CD'
        
        # Se não conseguir determinar, usar CD como padrão
        return 'CD'
    
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
    
    def _processar_data(self, data_str: str) -> Optional[str]:
        """
        Processa string de data para formato compatível com DateField.
        
        Args:
            data_str: String da data no formato da API
            
        Returns:
            String no formato YYYY-MM-DD ou None se inválida
        """
        if not data_str:
            return None
            
        try:
            # Tentar diferentes formatos de data
            from datetime import datetime
            
            # Formato comum: "2023-01-15T00:00:00"
            if 'T' in data_str:
                data_str = data_str.split('T')[0]
            
            # Verificar se já está no formato correto
            if len(data_str) == 10 and data_str.count('-') == 2:
                # Validar se é uma data válida
                datetime.strptime(data_str, '%Y-%m-%d')
                return data_str
            
            # Outros formatos podem ser adicionados aqui
            logger.warning(f"Formato de data não reconhecido: {data_str}")
            return None
            
        except (ValueError, AttributeError) as e:
            logger.warning(f"Erro ao processar data '{data_str}': {e}")
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
            
            # Determinar casa inicial se não estiver definida
            casa_inicial_determinada = None
            if not proposicao.casa_inicial:
                casa_inicial_determinada = self._determinar_casa_inicial(
                    dados_senado, dados_camara
                )
                if casa_inicial_determinada:
                    proposicao.casa_inicial = casa_inicial_determinada
                    logger.info(f"Casa inicial determinada: {casa_inicial_determinada}")
            
            # Sempre atualizar IDs das APIs (para referência)
            if dados_senado:
                proposicao.sf_id = dados_senado.get('sf_id')
            if dados_camara:
                proposicao.cd_id = dados_camara.get('cd_id')
            
            # Implementar RN0001: Extrair autor e data_apresentacao apenas da casa iniciadora
            casa_inicial_para_dados = proposicao.casa_inicial or casa_inicial_determinada
            
            if casa_inicial_para_dados:
                if casa_inicial_para_dados in ['SF', 'EXECUTIVO'] and dados_senado:
                    # Usar dados do Senado se a casa inicial for SF ou EXECUTIVO
                    if not proposicao.autor and dados_senado.get('autor'):
                        proposicao.autor = dados_senado.get('autor')
                    if not proposicao.data_apresentacao and dados_senado.get('data_apresentacao'):
                        proposicao.data_apresentacao = dados_senado.get('data_apresentacao')
                    logger.info(f"Dados extraídos da API do Senado para casa inicial: {casa_inicial_para_dados}")
                
                elif casa_inicial_para_dados == 'CD' and dados_camara:
                    # Usar dados da Câmara se a casa inicial for CD
                    if not proposicao.autor and dados_camara.get('autor'):
                        proposicao.autor = dados_camara.get('autor')
                    if not proposicao.data_apresentacao and dados_camara.get('data_apresentacao'):
                        proposicao.data_apresentacao = dados_camara.get('data_apresentacao')
                    logger.info(f"Dados extraídos da API da Câmara para casa inicial: {casa_inicial_para_dados}")
                
                else:
                    # RN0003: Proposição não encontrada na API da casa iniciadora
                    logger.warning(f"Proposição não encontrada na API da casa iniciadora: {casa_inicial_para_dados}")
            
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
    
    def sincronizar_todas_proposicoes(self, limit: Optional[int] = None, force: bool = False) -> Dict[str, int]:
        """
        Sincroniza proposições com as APIs.
        
        Args:
            limit: Limite de proposições a processar (None para todas)
            force: Se True, sincroniza todas as proposições, mesmo as já sincronizadas
            
        Returns:
            Dict com estatísticas da sincronização
        """
        from .models import Proposicao
        
        if force:
            proposicoes = Proposicao.objects.all().order_by('created_at')
        else:
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
