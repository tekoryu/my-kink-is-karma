import logging
from datetime import datetime
from typing import Dict, Optional

import requests
from django.utils import timezone

from .api_config import APIConfig, RateLimiter

logger = logging.getLogger(__name__)


class ActivitySyncService:
    """
    Responsável por sincronizar histórico de atividades de proposições
    (Senado e Câmara), extraído de `apps.pauta.services.APISyncService`.
    """

    def __init__(self):
        self.rate_limiter = RateLimiter()

    # --- Senado ---
    def sincronizar_atividades_senado(self, proposicao) -> bool:
        if not proposicao.sf_id:
            logger.warning(f"Proposição {proposicao.identificador_completo} não possui sf_id")
            return False

        try:
            self.rate_limiter.rate_limit_senado()
            search_url = f"{APIConfig.SENADO_BASE_URL}/processo/{proposicao.sf_id}"

            response = requests.get(search_url, headers=APIConfig.DEFAULT_HEADERS, timeout=30)
            if response.status_code != 200:
                logger.warning(f"Erro ao buscar processo {proposicao.sf_id} no Senado: {response.status_code}")
                return False

            data = response.json()
            atividades_criadas = 0

            for autuacao in data.get('autuacoes', []):
                for informe in autuacao.get('informesLegislativos', []):
                    if 'documentosAssociados' in informe:
                        continue
                    if self._criar_atividade_senado(proposicao, informe):
                        atividades_criadas += 1

            logger.info(f"Sincronizadas {atividades_criadas} atividades do Senado para {proposicao.identificador_completo}")
            return True
        except Exception as e:
            logger.error(f"Erro ao sincronizar atividades do Senado para {proposicao.identificador_completo}: {e}")
            return False

    def _processar_data(self, data_str: Optional[str]) -> Optional[str]:
        if not data_str:
            return None
        try:
            if 'T' in data_str:
                data_str = data_str.split('T')[0]
            if len(data_str) == 10 and data_str.count('-') == 2:
                datetime.strptime(data_str, '%Y-%m-%d')
                return data_str
            return None
        except Exception:
            return None

    def _extrair_valor_nested(self, data: Dict, key1: str, key2: str):
        try:
            nested = data.get(key1, {})
            if isinstance(nested, dict):
                return nested.get(key2)
            return None
        except Exception:
            return None

    def _criar_atividade_senado(self, proposicao, informe: Dict) -> bool:
        from apps.pauta.models import SenadoActivityHistory
        try:
            id_informe = informe.get('id')
            if not id_informe:
                return False

            atividade, created = SenadoActivityHistory.objects.get_or_create(
                proposicao=proposicao,
                id_informe=id_informe,
                defaults={
                    'data': self._processar_data(informe.get('data')),
                    'descricao': informe.get('descricao', ''),
                    'colegiado_codigo': self._extrair_valor_nested(informe, 'colegiado', 'codigo'),
                    'colegiado_casa': self._extrair_valor_nested(informe, 'colegiado', 'casa'),
                    'colegiado_sigla': self._extrair_valor_nested(informe, 'colegiado', 'sigla'),
                    'colegiado_nome': self._extrair_valor_nested(informe, 'colegiado', 'nome'),
                    'ente_administrativo_id': self._extrair_valor_nested(informe, 'enteAdministrativo', 'id'),
                    'ente_administrativo_casa': self._extrair_valor_nested(informe, 'enteAdministrativo', 'casa'),
                    'ente_administrativo_sigla': self._extrair_valor_nested(informe, 'enteAdministrativo', 'sigla'),
                    'ente_administrativo_nome': self._extrair_valor_nested(informe, 'enteAdministrativo', 'nome'),
                    'id_situacao_iniciada': informe.get('idSituacaoIniciada'),
                    'sigla_situacao_iniciada': informe.get('siglaSituacaoIniciada'),
                }
            )

            if not created:
                atividade.data = self._processar_data(informe.get('data'))
                atividade.descricao = informe.get('descricao', '')
                atividade.colegiado_codigo = self._extrair_valor_nested(informe, 'colegiado', 'codigo')
                atividade.colegiado_casa = self._extrair_valor_nested(informe, 'colegiado', 'casa')
                atividade.colegiado_sigla = self._extrair_valor_nested(informe, 'colegiado', 'sigla')
                atividade.colegiado_nome = self._extrair_valor_nested(informe, 'colegiado', 'nome')
                atividade.ente_administrativo_id = self._extrair_valor_nested(informe, 'enteAdministrativo', 'id')
                atividade.ente_administrativo_casa = self._extrair_valor_nested(informe, 'enteAdministrativo', 'casa')
                atividade.ente_administrativo_sigla = self._extrair_valor_nested(informe, 'enteAdministrativo', 'sigla')
                atividade.ente_administrativo_nome = self._extrair_valor_nested(informe, 'enteAdministrativo', 'nome')
                atividade.id_situacao_iniciada = informe.get('idSituacaoIniciada')
                atividade.sigla_situacao_iniciada = informe.get('siglaSituacaoIniciada')
                atividade.save()

            return True
        except Exception as e:
            logger.error(f"Erro ao criar atividade do Senado: {e}")
            return False

    # --- Câmara ---
    def sincronizar_atividades_camara(self, proposicao) -> bool:
        if not proposicao.cd_id:
            logger.warning(f"Proposição {proposicao.identificador_completo} não possui cd_id")
            return False

        try:
            self.rate_limiter.rate_limit_camara()
            tramitacoes_url = f"{APIConfig.CAMARA_BASE_URL}/proposicoes/{proposicao.cd_id}/tramitacoes"

            response = requests.get(tramitacoes_url, headers=APIConfig.DEFAULT_HEADERS, timeout=30)
            if response.status_code != 200:
                logger.warning(f"Erro ao buscar tramitações {proposicao.cd_id} na Câmara: {response.status_code}")
                return False

            data = response.json()
            atividades_criadas = 0
            for tramitacao in data.get('dados', []):
                if self._criar_atividade_camara(proposicao, tramitacao):
                    atividades_criadas += 1

            logger.info(f"Sincronizadas {atividades_criadas} atividades da Câmara para {proposicao.identificador_completo}")
            return True
        except Exception as e:
            logger.error(f"Erro ao sincronizar atividades da Câmara para {proposicao.identificador_completo}: {e}")
            return False

    def _criar_atividade_camara(self, proposicao, tramitacao: Dict) -> bool:
        from apps.pauta.models import CamaraActivityHistory
        try:
            sequencia = tramitacao.get('sequencia')
            if not sequencia:
                return False

            data_hora_str = tramitacao.get('dataHora')
            data_hora = None
            if data_hora_str:
                try:
                    if 'T' in data_hora_str:
                        naive_datetime = datetime.strptime(data_hora_str, '%Y-%m-%dT%H:%M')
                    else:
                        naive_datetime = datetime.strptime(data_hora_str, '%Y-%m-%d')
                    data_hora = timezone.make_aware(naive_datetime, timezone=timezone.get_current_timezone())
                except ValueError:
                    logger.warning(f"Formato de data inválido: {data_hora_str}")

            atividade, created = CamaraActivityHistory.objects.get_or_create(
                proposicao=proposicao,
                sequencia=sequencia,
                defaults={
                    'data_hora': data_hora,
                    'sigla_orgao': tramitacao.get('siglaOrgao', ''),
                    'uri_orgao': tramitacao.get('uriOrgao'),
                    'uri_ultimo_relator': tramitacao.get('uriUltimoRelator'),
                    'regime': tramitacao.get('regime'),
                    'descricao_tramitacao': tramitacao.get('descricaoTramitacao', ''),
                    'cod_tipo_tramitacao': tramitacao.get('codTipoTramitacao', ''),
                    'descricao_situacao': tramitacao.get('descricaoSituacao'),
                    'cod_situacao': tramitacao.get('codSituacao'),
                    'despacho': tramitacao.get('despacho', ''),
                    'url': tramitacao.get('url'),
                    'ambito': tramitacao.get('ambito'),
                    'apreciacao': tramitacao.get('apreciacao'),
                }
            )

            if not created:
                atividade.data_hora = data_hora
                atividade.sigla_orgao = tramitacao.get('siglaOrgao', '')
                atividade.uri_orgao = tramitacao.get('uriOrgao')
                atividade.uri_ultimo_relator = tramitacao.get('uriUltimoRelator')
                atividade.regime = tramitacao.get('regime')
                atividade.descricao_tramitacao = tramitacao.get('descricaoTramitacao', '')
                atividade.cod_tipo_tramitacao = tramitacao.get('codTipoTramitacao', '')
                atividade.descricao_situacao = tramitacao.get('descricaoSituacao')
                atividade.cod_situacao = tramitacao.get('codSituacao')
                atividade.despacho = tramitacao.get('despacho', '')
                atividade.url = tramitacao.get('url')
                atividade.ambito = tramitacao.get('ambito')
                atividade.apreciacao = tramitacao.get('apreciacao')
                atividade.save()

            return True
        except Exception as e:
            logger.error(f"Erro ao criar atividade da Câmara: {e}")
            return False


