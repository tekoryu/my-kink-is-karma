import logging
from typing import Dict

logger = logging.getLogger(__name__)


class SelectionService:
    """
    Lógica de seleção de proposições por tema, extraída de `APISyncService`.
    """

    def atualizar_selecao_tema(self, tema) -> bool:
        try:
            from apps.pauta.models import Proposicao
            Proposicao.objects.filter(tema=tema).update(selected=False)

            proposicoes = Proposicao.objects.filter(tema=tema).filter(
                data_apresentacao__isnull=False
            ).order_by('data_apresentacao', 'id')

            if proposicoes.exists():
                proposicao_selecionada = proposicoes.first()
                proposicao_selecionada.selected = True
                proposicao_selecionada.save()
                logger.info(f"Tema '{tema.nome}': selecionada proposição {proposicao_selecionada.identificador_completo}")
                return True
            else:
                proposicoes_sem_data = Proposicao.objects.filter(tema=tema).order_by('id')
                if proposicoes_sem_data.exists():
                    proposicao_selecionada = proposicoes_sem_data.first()
                    proposicao_selecionada.selected = True
                    proposicao_selecionada.save()
                    logger.info(f"Tema '{tema.nome}': selecionada proposição {proposicao_selecionada.identificador_completo} (sem data)")
                    return True
                else:
                    logger.warning(f"Tema '{tema.nome}': não possui proposições para selecionar")
                    return False
        except Exception as e:
            logger.error(f"Erro ao atualizar seleção do tema '{tema.nome}': {e}")
            return False

    def atualizar_selecao_proposicoes(self) -> Dict[str, int]:
        from apps.pauta.models import Proposicao, Tema
        total_temas = 0
        total_atualizadas = 0
        erros = 0

        logger.info("Iniciando atualização de seleção de proposições por tema")
        try:
            temas = Tema.objects.filter(proposicoes__isnull=False).distinct()
            total_temas = temas.count()
            for tema in temas:
                try:
                    Proposicao.objects.filter(tema=tema).update(selected=False)

                    proposicoes = Proposicao.objects.filter(tema=tema).filter(
                        data_apresentacao__isnull=False
                    ).order_by('data_apresentacao', 'id')

                    if proposicoes.exists():
                        proposicao_selecionada = proposicoes.first()
                        proposicao_selecionada.selected = True
                        proposicao_selecionada.save()
                        total_atualizadas += 1
                        logger.info(f"Tema '{tema.nome}': selecionada proposição {proposicao_selecionada.identificador_completo}")
                    else:
                        proposicoes_sem_data = Proposicao.objects.filter(tema=tema).order_by('id')
                        if proposicoes_sem_data.exists():
                            proposicao_selecionada = proposicoes_sem_data.first()
                            proposicao_selecionada.selected = True
                            proposicao_selecionada.save()
                            total_atualizadas += 1
                            logger.info(f"Tema '{tema.nome}': selecionada proposição {proposicao_selecionada.identificador_completo} (sem data)")
                        else:
                            logger.warning(f"Tema '{tema.nome}': não possui proposições para selecionar")
                except Exception as e:
                    logger.error(f"Erro ao processar tema '{tema.nome}': {e}")
                    erros += 1

            logger.info(f"Atualização de seleção concluída: {total_atualizadas} proposições selecionadas em {total_temas} temas, {erros} erros")
            return {
                'total_temas': total_temas,
                'total_atualizadas': total_atualizadas,
                'erros': erros
            }
        except Exception as e:
            logger.error(f"Erro na atualização de seleção de proposições: {e}")
            return {
                'total_temas': 0,
                'total_atualizadas': 0,
                'erros': 1
            }


