import requests
import logging
from typing import Dict, Optional
from .models import HistoricoAtualizacao

logger = logging.getLogger(__name__)

def consultar_e_salvar_dados_iniciais(proposicao):
    """
    Consulta dados iniciais de uma proposição na API SF_API e salva no histórico.
    
    Args:
        proposicao: Instância do modelo Proposicao
        
    Returns:
        Dict: Dados da proposição retornados pela API ou None em caso de falha
    """
    try:
        # Construir URL da API SF
        base_url = "https://legis.senado.leg.br/dadosabertos/processo"
        
        # Parâmetros para busca da proposição
        params = {
            'sigla': proposicao.tipo,
            'numero': proposicao.numero,
            'ano': proposicao.ano,
            'v': 1  # Versão da API
        }
        
        # Headers para aceitar JSON
        headers = {
            'Accept': 'application/json'
        }
        
        logger.info(f"Consultando SF_API para proposição {proposicao.identificador_completo}")
        
        # Fazer requisição para a API
        response = requests.get(base_url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Parsear resposta JSON
        dados = response.json()
        
        # Verificar se encontrou dados
        if not dados or not isinstance(dados, list) or len(dados) == 0:
            logger.warning(f"Nenhum dado encontrado para {proposicao.identificador_completo}")
            return None
        
        # Pegar o primeiro resultado (deve ser único para a combinação tipo/numero/ano)
        dados_proposicao = dados[0]
        
        # Salvar no histórico de atualização
        HistoricoAtualizacao.objects.create(
            proposicao=proposicao,
            dados_atualizados=dados_proposicao
        )
        
        logger.info(f"Dados salvos com sucesso para {proposicao.identificador_completo}")
        
        return dados_proposicao
        
    except requests.RequestException as e:
        logger.error(f"Erro de requisição para {proposicao.identificador_completo}: {e}")
        return None
    except Exception as e:
        logger.error(f"Erro inesperado ao consultar API para {proposicao.identificador_completo}: {e}")
        return None

def consultar_api_proposicao(proposicao) -> Optional[Dict]:
    """
    Consulta a API externa para obter dados atualizados de uma proposição.
    
    Args:
        proposicao: Instância do modelo Proposicao
        
    Returns:
        Dict: Dados da proposição retornados pela API ou None se não encontrada
    """
    try:
        # TODO: Implementar consulta real à API pública
        # Por enquanto, retorna dados mockados para teste
        dados_mock = {
            'tipo': proposicao.tipo,
            'numero': proposicao.numero,
            'ano': proposicao.ano,
            'status': 'Em tramitação',
            'ultima_atualizacao': '2024-01-15T10:30:00Z',
            'situacao': 'Aguardando parecer',
            'comissoes': ['CCJ', 'CE'],
            'autores': ['Dep. João Silva'],
            'ementa': 'Dispõe sobre...'
        }
        
        logger.info(f"Consultando API para proposição {proposicao.identificador_completo}")
        return dados_mock
        
    except requests.RequestException as e:
        logger.error(f"Erro ao consultar API para {proposicao.identificador_completo}: {e}")
        return None
    except Exception as e:
        logger.error(f"Erro inesperado ao consultar API para {proposicao.identificador_completo}: {e}")
        return None 