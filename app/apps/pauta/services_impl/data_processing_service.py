import logging
from typing import Optional, Dict

from django.db.models import Max, Min

logger = logging.getLogger(__name__)


class DataProcessingService:
    """
    Serviços de processamento e enriquecimento de dados das proposições.

    Objetivos:
    - Preencher campos derivados (ex: current_house) com base nas atividades.
    - Realizar backfill de datas e campos quando possível a partir do histórico.
    - Executar rotinas em lote de processamento.
    """

    def update_derived_fields(self, proposicao) -> bool:
        """
        Atualiza campos derivados de uma `Proposicao` (ex.: current_house) a partir do histórico.
        """
        try:
            from apps.pauta.models import SenadoActivityHistory, CamaraActivityHistory

            # Última atividade em cada casa
            ultima_sf = (
                SenadoActivityHistory.objects
                .filter(proposicao=proposicao)
                .aggregate(ultima=Max('data'))
                .get('ultima')
            )
            ultima_cd = (
                CamaraActivityHistory.objects
                .filter(proposicao=proposicao)
                .aggregate(ultima=Max('data_hora'))
                .get('ultima')
            )

            novo_current_house: Optional[str] = None
            if ultima_sf and ultima_cd:
                # Comparar datas para decidir a casa com atividade mais recente
                if ultima_cd > ultima_sf:
                    novo_current_house = 'CD'
                else:
                    novo_current_house = 'SF'
            elif ultima_cd:
                novo_current_house = 'CD'
            elif ultima_sf:
                novo_current_house = 'SF'

            if novo_current_house and proposicao.current_house != novo_current_house:
                proposicao.current_house = novo_current_house
                proposicao.save(update_fields=['current_house'])
                logger.info(
                    f"Atualizado current_house de {proposicao.identificador_completo} para {novo_current_house}"
                )

            # Backfill de data_apresentacao se ausente: pegar a mais antiga conhecida
            if not proposicao.data_apresentacao:
                primeira_sf = (
                    SenadoActivityHistory.objects
                    .filter(proposicao=proposicao)
                    .aggregate(primeira=Min('data'))
                    .get('primeira')
                )
                primeira_cd_date = (
                    CamaraActivityHistory.objects
                    .filter(proposicao=proposicao)
                    .aggregate(primeira=Min('data_hora'))
                    .get('primeira')
                )
                # Converter datetime -> date quando necessário
                if primeira_cd_date:
                    primeira_cd = primeira_cd_date.date()
                else:
                    primeira_cd = None

                candidates = [d for d in [primeira_sf, primeira_cd] if d is not None]
                if candidates:
                    nova_data = min(candidates)
                    proposicao.data_apresentacao = nova_data
                    proposicao.save(update_fields=['data_apresentacao'])
                    logger.info(
                        f"Backfill data_apresentacao de {proposicao.identificador_completo} para {nova_data}"
                    )

            return True
        except Exception as e:
            logger.error(f"Erro ao atualizar campos derivados de {proposicao}: {e}")
            return False

    def processar_todas_proposicoes(self, limit: Optional[int] = None) -> Dict[str, int]:
        """
        Executa processamento de campos derivados para várias proposições.
        """
        from apps.pauta.models import Proposicao

        qs = Proposicao.objects.all().order_by('created_at')
        if limit:
            qs = qs[:limit]

        total = qs.count()
        sucesso = 0
        erros = 0

        for prop in qs:
            if self.update_derived_fields(prop):
                sucesso += 1
            else:
                erros += 1

        return {'total': total, 'sucesso': sucesso, 'erros': erros}


