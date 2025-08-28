import requests
import json
import time
from datetime import datetime
from typing import Dict, Optional, List
from django.utils import timezone
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

from .services_impl.activity_sync_service import ActivitySyncService
from .services_impl.selection_service import SelectionService
from .services_impl import DataProcessingService
from .services_impl.api_config import APIConfig, RateLimiter

class APISyncService:
    """
    Serviço para sincronização de dados das APIs do Senado Federal e Câmara dos Deputados.
    Implementa busca estruturada:
    1. Busca no Senado Federal para encontrar sf_id e determinar se é casa iniciadora
    2. Para proposições sem iniciadora definida, busca na Câmara dos Deputados
    """
    
    def __init__(self):
        # Shared rate limiter for all API calls
        self.rate_limiter = RateLimiter()
        # Delegated services
        self.activity_sync = ActivitySyncService()
        self.selection = SelectionService()
        self.data_processing = DataProcessingService()
    
    def buscar_proposicao_senado(self, tipo: str, numero: int, ano: int) -> Optional[Dict]:
        """
        Busca uma proposição na API do Senado Federal usando endpoint /processo.
        
        Args:
            tipo: Tipo da proposição (PL, PEC, etc.)
            numero: Número da proposição
            ano: Ano da proposição
            
        Returns:
            Dict com sf_id, data_apresentacao, ementa, casa_iniciadora, autor se encontrada
        """
        self.rate_limiter.rate_limit_senado()
        
        search_url = f"{APIConfig.SENADO_BASE_URL}/processo"
        
        params = {
            'sigla': tipo,
            'numero': numero,
            'ano': ano
        }
        
        try:
            response = requests.get(
                search_url, 
                params=params,
                headers=APIConfig.DEFAULT_HEADERS, 
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
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
        Primeiro busca na listagem, depois busca detalhes completos.
        
        Args:
            tipo: Tipo da proposição (PL, PEC, etc.)
            numero: Número da proposição
            ano: Ano da proposição
            
        Returns:
            Dict com cd_id, iniciadora='CD', ementa, data_apresentacao, autor se encontrada
        """
        self.rate_limiter.rate_limit_camara()
        
        # Primeiro: buscar na listagem para obter o ID
        search_url = f"{APIConfig.CAMARA_BASE_URL}/proposicoes"
        
        params = {
            'siglaTipo': tipo,
            'numero': numero,
            'ano': ano
        }
        
        try:
            response = requests.get(
                search_url, 
                params=params, 
                headers=APIConfig.DEFAULT_HEADERS, 
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'dados' in data and len(data['dados']) > 0:
                    cd_id = data['dados'][0]['id']
                    return self._buscar_detalhes_proposicao_camara(cd_id)
                else:
                    logger.info(f"Proposição {tipo} {numero}/{ano} não encontrada na Câmara")
                    return None
            else:
                logger.warning(f"Erro ao buscar proposição na Câmara: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição para API da Câmara: {e}")
            return None
    
    def _processar_resposta_senado(self, data: List, tipo: str, numero: int, ano: int) -> Optional[Dict]:
        """
        Processa a resposta da API do Senado e extrai os dados necessários.
        Busca pelo processo específico e verifica se objetivo='Iniciadora' para determinar iniciadora.
        """
        try:
            if not isinstance(data, list):
                return None
            
            # Procurar pela proposição específica baseada no tipo, número e ano
            for processo in data:
                identificacao = processo.get('identificacao', '')
                
                # Verificar se a identificação contém o tipo, número e ano
                if (tipo in identificacao and 
                    str(numero) in identificacao and 
                    str(ano) in identificacao):
                    
                    # Extrair dados básicos
                    sf_id = processo.get('id')
                    data_apresentacao = self._processar_data_senado(processo)
                    ementa = self._extrair_ementa_senado(processo)
                    
                    # Verificar se é casa iniciadora
                    objetivo = processo.get('objetivo', '')
                    iniciadora = None
                    autor = None
                    
                    if objetivo == 'Iniciadora':
                        iniciadora = 'SF'
                        autor = self._extrair_autor_senado(processo)
                    
                    return {
                        'sf_id': sf_id,
                        'data_apresentacao': data_apresentacao,
                        'ementa': ementa,
                        'iniciadora': iniciadora,
                        'autor': autor
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao processar resposta do Senado: {e}")
            return None
    
    def _buscar_detalhes_proposicao_camara(self, cd_id: int) -> Optional[Dict]:
        """
        Busca detalhes completos de uma proposição na Câmara usando seu ID.
        """
        self.rate_limiter.rate_limit_camara()
        
        # Buscar detalhes da proposição
        details_url = f"{APIConfig.CAMARA_BASE_URL}/proposicoes/{cd_id}"
        
        try:
            response = requests.get(details_url, headers=APIConfig.DEFAULT_HEADERS, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if 'dados' in data:
                    proposicao = data['dados']
                    
                    # Extrair dados básicos
                    ementa = proposicao.get('ementa')
                    data_apresentacao = self._processar_data_camara(proposicao.get('dataApresentacao'))
                    
                    # Buscar autores
                    autor = self._buscar_autor_camara(cd_id)
                    
                    return {
                        'cd_id': cd_id,
                        'iniciadora': 'CD',  # Assumimos CD para proposições sem iniciadora do SF
                        'ementa': ementa,
                        'data_apresentacao': data_apresentacao,
                        'autor': autor
                    }
            
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao buscar detalhes da proposição {cd_id}: {e}")
            return None
    
    def _processar_data_senado(self, processo: Dict) -> Optional[str]:
        """
        Extrai a data de apresentação do processo do Senado.
        """
        try:
            data_str = processo.get('dataApresentacao')
            return self._processar_data(data_str)
        except Exception:
            return None
    
    def _processar_data_camara(self, data_str: str) -> Optional[str]:
        """
        Processa data de apresentação da Câmara (formato 2023-09-11T12:24).
        """
        if not data_str:
            return None
        try:
            # Remover a parte de hora se presente
            if 'T' in data_str:
                data_str = data_str.split('T')[0]
            # Verificar se já está no formato correto
            datetime.strptime(data_str, '%Y-%m-%d')
            return data_str
        except (ValueError, AttributeError):
            return None
    
    def _extrair_ementa_senado(self, processo: Dict) -> Optional[str]:
        """
        Extrai a ementa do processo do Senado.
        """
        try:
            return processo.get('ementa')
        except Exception:
            return None
    
    def _extrair_autor_senado(self, processo: Dict) -> Optional[str]:
        """
        Extrai o autor do processo do Senado da estrutura de autoria.
        """
        try:
            autoria = processo.get('autoria')
            return autoria if isinstance(autoria, str) else None
        except Exception:
            return None
    
    def _buscar_autor_camara(self, cd_id: int) -> Optional[str]:
        """
        Busca o autor de uma proposição na Câmara e formata adequadamente.
        """
        self.rate_limiter.rate_limit_camara()
        
        autores_url = f"{APIConfig.CAMARA_BASE_URL}/proposicoes/{cd_id}/autores"
        
        try:
            response = requests.get(autores_url, headers=APIConfig.DEFAULT_HEADERS, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if 'dados' in data and len(data['dados']) > 0:
                    nome = data['dados'][0].get('nome', '')

                    return nome
            
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao buscar autores da proposição {cd_id}: {e}")
            return None
    
    def _buscar_dados_deputado(self, uri: str) -> Optional[str]:
        """
        Busca dados completos do deputado e formata nome conforme especificação.
        """
        self.rate_limiter.rate_limit_camara()
        
        try:
            response = requests.get(uri, headers=APIConfig.DEFAULT_HEADERS, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if 'dados' in data:
                    deputado = data['dados']
                    ultimo_status = deputado.get('ultimoStatus', {})
                    
                    nome_eleitoral = ultimo_status.get('nomeEleitoral', '')
                    sigla_partido = ultimo_status.get('siglaPartido', '')
                    sigla_uf = ultimo_status.get('siglaUf', '')
                    sexo = deputado.get('sexo', 'M')
                    
                    if nome_eleitoral and sigla_partido and sigla_uf:
                        titulo = "Deputada" if sexo == 'F' else "Deputado"
                        return f"{titulo} {nome_eleitoral} ({sigla_partido}/{sigla_uf})"
                    
                    return nome_eleitoral or deputado.get('nomeCivil', '')
            
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao buscar dados do deputado {uri}: {e}")
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

    def sincronizar_proposicao(self, proposicao) -> bool:
        """
        Sincroniza uma proposição específica com as APIs seguindo a nova estratégia:
        1. Busca no Senado para sf_id e verifica se é casa iniciadora
        2. Se não tem iniciadora definida, busca na Câmara
        
        Args:
            proposicao: Instância do modelo Proposicao
            
        Returns:
            bool: True se a sincronização foi bem-sucedida, False caso contrário
        """
        try:
            logger.info(f"Sincronizando proposição: {proposicao.identificador_completo}")
            
            dados_camara = None
            encontrou_dados = False
            
            # Etapa 1: Buscar no Senado Federal
            dados_senado = self.buscar_proposicao_senado(
                proposicao.tipo, proposicao.numero, proposicao.ano
            )
            
            # Sempre salvar sf_id se encontrado
            if dados_senado and dados_senado.get('sf_id'):
                proposicao.sf_id = dados_senado['sf_id']
                logger.info(f"SF ID encontrado: {dados_senado['sf_id']}")
                encontrou_dados = True
            
            # Se o Senado indicou que é casa iniciadora, usar seus dados
            if dados_senado and dados_senado.get('iniciadora') == 'SF':
                proposicao.iniciadora = 'SF'
                if dados_senado.get('autor'):
                    proposicao.autor = dados_senado['autor']
                if dados_senado.get('data_apresentacao'):
                    proposicao.data_apresentacao = dados_senado['data_apresentacao']
                if dados_senado.get('ementa'):
                    proposicao.ementa = dados_senado['ementa']
                logger.info("Dados extraídos do Senado (casa iniciadora)")
                encontrou_dados = True
            
            # Etapa 2: Se não tem iniciadora definida, buscar na Câmara
            if not proposicao.iniciadora:
                dados_camara = self.buscar_proposicao_camara(
                    proposicao.tipo, proposicao.numero, proposicao.ano
                )
                
                if dados_camara:
                    # Salvar cd_id
                    if dados_camara.get('cd_id'):
                        proposicao.cd_id = dados_camara['cd_id']
                        logger.info(f"CD ID encontrado: {dados_camara['cd_id']}")
                        encontrou_dados = True

                    
                    # Assumir que é casa inicial = CD
                    proposicao.iniciadora = 'CD'
                    
                    # Extrair dados da Câmara
                    if dados_camara.get('autor'):
                        proposicao.autor = dados_camara['autor']
                    if dados_camara.get('data_apresentacao'):
                        proposicao.data_apresentacao = dados_camara['data_apresentacao']
                    if dados_camara.get('ementa'):
                        proposicao.ementa = dados_camara['ementa']
                    
                    logger.info("Dados extraídos da Câmara (casa inicial determinada como CD)")
                    encontrou_dados = True
            
            # Verificar se a proposição foi encontrada em alguma API
            if not encontrou_dados:
                # Proposição não encontrada em nenhuma API
                proposicao.ultima_sincronizacao = None
                proposicao.erro_sincronizacao = 'NOT FOUND'
                proposicao.save()
                logger.warning(f"Proposição {proposicao.identificador_completo} não encontrada em nenhuma API")
                return False
            else:
                # Marcar como sincronizada com sucesso
                proposicao.ultima_sincronizacao = timezone.now()
                proposicao.erro_sincronizacao = None
                proposicao.save()
                logger.info(f"Proposição {proposicao.identificador_completo} sincronizada com sucesso")
                
                # Atualizar seleção do tema automaticamente
                try:
                    self.atualizar_selecao_tema(proposicao.tema)
                    logger.debug(f"Seleção atualizada para tema '{proposicao.tema.nome}' após sincronização")
                except Exception as e:
                    logger.warning(f"Erro ao atualizar seleção do tema após sincronização: {e}")
                
                # Atualizar campos derivados (ex.: current_house, data backfill)
                try:
                    self.data_processing.update_derived_fields(proposicao)
                except Exception as e:
                    logger.warning(f"Erro ao atualizar campos derivados após sincronização: {e}")

                return True
            
        except Exception as e:
            logger.error(f"Erro ao sincronizar proposição {proposicao.identificador_completo}: {e}")
            proposicao.erro_sincronizacao = str(e)
            proposicao.ultima_sincronizacao = None
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
        
        # Atualizar seleção de todas as proposições após sincronização em lote
        if sucessos > 0:
            try:
                logger.info("Atualizando seleção de proposições após sincronização em lote")
                selecao_result = self.atualizar_selecao_proposicoes()
                logger.info(f"Seleção atualizada: {selecao_result}")
            except Exception as e:
                logger.warning(f"Erro ao atualizar seleção após sincronização em lote: {e}")
        
        return {
            'total': total,
            'sucessos': sucessos,
            'erros': erros
        }

    def sincronizar_atividades_senado(self, proposicao) -> bool:
        """Delegates to ActivitySyncService."""
        return self.activity_sync.sincronizar_atividades_senado(proposicao)
    
    def sincronizar_atividades_camara(self, proposicao) -> bool:
        """Delegates to ActivitySyncService."""
        return self.activity_sync.sincronizar_atividades_camara(proposicao)
    
    def _criar_atividade_senado(self, proposicao, informe: Dict) -> bool:
        """Backward-compat shim: delegate to ActivitySyncService."""
        return self.activity_sync._criar_atividade_senado(proposicao, informe)
    
    def _criar_atividade_camara(self, proposicao, tramitacao: Dict) -> bool:
        """Backward-compat shim: delegate to ActivitySyncService."""
        return self.activity_sync._criar_atividade_camara(proposicao, tramitacao)
       
    def sincronizar_atividades_todas_proposicoes(self, limit: Optional[int] = None) -> Dict[str, int]:
        """
        Sincroniza atividades de todas as proposições que possuem IDs das APIs.
        
        Args:
            limit: Limite de proposições a processar (None para todas)
            
        Returns:
            Dict com estatísticas da sincronização
        """
        from .models import Proposicao
        
        proposicoes = Proposicao.objects.filter(
            sf_id__isnull=False
        ).order_by('created_at')
        
        if limit:
            proposicoes = proposicoes[:limit]
        
        total = proposicoes.count()
        sucessos_senado = 0
        sucessos_camara = 0
        erros = 0
        
        logger.info(f"Iniciando sincronização de atividades para {total} proposições")
        
        for proposicao in proposicoes:
            try:
                # Sincronizar atividades do Senado se tem sf_id
                if proposicao.sf_id:
                    if self.activity_sync.sincronizar_atividades_senado(proposicao):
                        sucessos_senado += 1
                    else:
                        erros += 1
                
                # Sincronizar atividades da Câmara se tem cd_id
                if proposicao.cd_id:
                    if self.activity_sync.sincronizar_atividades_camara(proposicao):
                        sucessos_camara += 1
                    else:
                        erros += 1
                
                # Pausa entre proposições
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Erro ao sincronizar atividades para {proposicao.identificador_completo}: {e}")
                erros += 1
        
        logger.info(f"Sincronização de atividades concluída: {sucessos_senado} Senado, {sucessos_camara} Câmara, {erros} erros")
        
        return {
            'total': total,
            'sucessos_senado': sucessos_senado,
            'sucessos_camara': sucessos_camara,
            'erros': erros
        }
    
    def atualizar_selecao_tema(self, tema) -> bool:
        """Delegates to SelectionService."""
        return self.selection.atualizar_selecao_tema(tema)

    def atualizar_selecao_proposicoes(self) -> Dict[str, int]:
        """Delegates to SelectionService."""
        return self.selection.atualizar_selecao_proposicoes()