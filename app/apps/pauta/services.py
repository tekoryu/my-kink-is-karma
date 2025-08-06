import requests
import logging
from typing import Dict, Optional
from django.utils import timezone
from datetime import datetime
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
        }
        
        # Headers para aceitar JSON
        headers = {
            'Accept': 'application/json'
        }
        
        logger.info(f"Consultando SF_API para proposição {proposicao.identificador_completo}")
        
        # Fazer requisição para a API
        response = requests.get(base_url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Verificar o tipo de conteúdo retornado
        content_type = response.headers.get('content-type', '')
        
        if 'application/json' in content_type:
            # Parsear resposta JSON
            dados = response.json()
        else:
            # Se não for JSON, retornar o texto como está
            dados = response.text
            logger.warning(f"API retornou {content_type} em vez de JSON para {proposicao.identificador_completo}")
            return dados
        
        # Verificar se encontrou dados
        if not dados or not isinstance(dados, list) or len(dados) == 0:
            logger.warning(f"Nenhum dado encontrado para {proposicao.identificador_completo}")
            return None
        
        # Pegar o primeiro resultado (deve ser único para a combinação tipo/numero/ano)
        dados_proposicao = dados[0]

        # Atualizar campos da Proposicao com dados da API
        _atualizar_campos_proposicao(proposicao, dados_proposicao)
        
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


def _atualizar_campos_proposicao(proposicao, dados):
    """
    Atualiza os campos da Proposicao com dados da API SF.
    
    Args:
        proposicao: Instância do modelo Proposicao
        dados: Dicionário com dados da API
    """
    try:
        # Mapeamento de campos da API para campos do modelo
        campos_para_atualizar = {}
        
        # Campos básicos
        if 'id' in dados:
            campos_para_atualizar['sf_id'] = dados['id']
        
        if 'codigoMateria' in dados:
            campos_para_atualizar['sf_codigo_materia'] = dados['codigoMateria']
        
        if 'papel' in dados:
            campos_para_atualizar['papel_sf'] = dados['papel']
        
        if 'tipoConteudo' in dados:
            campos_para_atualizar['tipo_conteudo'] = dados['tipoConteudo']
        
        if 'ementa' in dados:
            campos_para_atualizar['ementa'] = dados['ementa']
        
        if 'tipoDocumento' in dados:
            campos_para_atualizar['tipo_documento'] = dados['tipoDocumento']
        
        if 'dataApresentacao' in dados:
            try:
                # Parse the date string for presentation date
                if isinstance(dados['dataApresentacao'], str):
                    # Try different date formats for date only
                    for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%Y-%m-%d %H:%M:%S']:
                        try:
                            parsed_date = datetime.strptime(dados['dataApresentacao'], fmt)
                            campos_para_atualizar['sf_data_apresentacao'] = parsed_date.date()
                            break
                        except ValueError:
                            continue
                    else:
                        logger.warning(f"Could not parse presentation date: {dados['dataApresentacao']}")
                else:
                    # If it's already a date/datetime object
                    if hasattr(dados['dataApresentacao'], 'date'):
                        campos_para_atualizar['sf_data_apresentacao'] = dados['dataApresentacao'].date()
                    else:
                        campos_para_atualizar['sf_data_apresentacao'] = dados['dataApresentacao']
            except Exception as e:
                logger.warning(f"Error parsing presentation date {dados['dataApresentacao']}: {e}")
        
        if 'autoria' in dados:
            campos_para_atualizar['sf_autoria'] = dados['autoria']
        
        if 'tramitando' in dados:
            campos_para_atualizar['sf_tramitando'] = dados['tramitando']
        
        if 'ultimaInformacaoAtualizada' in dados:
            campos_para_atualizar['sf_last_info'] = dados['ultimaInformacaoAtualizada']
        
        if 'dataUltimaAtualizacao' in dados:
            try:
                # Parse the date string and make it timezone-aware
                if isinstance(dados['dataUltimaAtualizacao'], str):
                    # Try different date formats
                    for fmt in ['%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d']:
                        try:
                            parsed_date = datetime.strptime(dados['dataUltimaAtualizacao'], fmt)
                            campos_para_atualizar['sf_lastupdate_date'] = timezone.make_aware(parsed_date)
                            break
                        except ValueError:
                            continue
                    else:
                        # If no format matches, use current timezone
                        logger.warning(f"Could not parse date: {dados['dataUltimaAtualizacao']}")
                        campos_para_atualizar['sf_lastupdate_date'] = timezone.now()
                else:
                    # If it's already a datetime object, make it timezone-aware
                    campos_para_atualizar['sf_lastupdate_date'] = timezone.make_aware(dados['dataUltimaAtualizacao'])
            except Exception as e:
                logger.warning(f"Error parsing date {dados['dataUltimaAtualizacao']}: {e}")
                campos_para_atualizar['sf_lastupdate_date'] = timezone.now()
        
        # Atualizar apenas se há campos para atualizar
        if campos_para_atualizar:
            for campo, valor in campos_para_atualizar.items():
                setattr(proposicao, campo, valor)
            
            proposicao.save(update_fields=list(campos_para_atualizar.keys()))
            logger.info(f"Campos atualizados para {proposicao.identificador_completo}: {list(campos_para_atualizar.keys())}")
        
    except Exception as e:
        logger.error(f"Erro ao atualizar campos da proposição {proposicao.identificador_completo}: {e}")
        raise

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