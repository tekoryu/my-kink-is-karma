from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from apps.pauta.services import APISyncService
from apps.pauta.models import Proposicao
from apps.core.logging_utils import log_database_operation, log_error, log_performance
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Sincroniza o histórico de atividades das proposições com as APIs do Senado e Câmara'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            help='Limite de proposições a processar'
        )
        parser.add_argument(
            '--proposicao-id',
            type=int,
            help='ID específico de uma proposição para sincronizar'
        )
        parser.add_argument(
            '--senado-only',
            action='store_true',
            help='Sincronizar apenas atividades do Senado'
        )
        parser.add_argument(
            '--camara-only',
            action='store_true',
            help='Sincronizar apenas atividades da Câmara'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forçar sincronização mesmo se já existem dados'
        )

    def handle(self, *args, **options):
        try:
            import time
            start_time = time.time()
            
            self.stdout.write(
                self.style.SUCCESS('Iniciando sincronização de histórico de atividades...')
            )
            
            # Inicializar serviço
            sync_service = APISyncService()
            
            # Determinar proposições a processar
            if options['proposicao_id']:
                try:
                    proposicoes = [Proposicao.objects.get(id=options['proposicao_id'])]
                    self.stdout.write(f"Processando proposição específica: {proposicoes[0].identificador_completo}")
                except Proposicao.DoesNotExist:
                    raise CommandError(f"Proposição com ID {options['proposicao_id']} não encontrada")
            else:
                # Filtrar proposições com IDs das APIs
                proposicoes = Proposicao.objects.filter(
                    sf_id__isnull=False
                ).order_by('created_at')
                
                if options['limit']:
                    proposicoes = proposicoes[:options['limit']]
                
                self.stdout.write(f"Processando {proposicoes.count()} proposições")
            
            # Contadores
            total = len(proposicoes)
            sucessos_senado = 0
            sucessos_camara = 0
            erros = 0
            
            # Processar cada proposição
            for i, proposicao in enumerate(proposicoes, 1):
                self.stdout.write(f"[{i}/{total}] Processando {proposicao.identificador_completo}...")
                
                try:
                    # Sincronizar atividades do Senado
                    if not options['camara_only'] and proposicao.sf_id:
                        if sync_service.sincronizar_atividades_senado(proposicao):
                            sucessos_senado += 1
                            self.stdout.write(
                                self.style.SUCCESS(f"  ✓ Senado: OK")
                            )
                        else:
                            erros += 1
                            self.stdout.write(
                                self.style.WARNING(f"  ✗ Senado: ERRO")
                            )
                    
                    # Sincronizar atividades da Câmara
                    if not options['senado_only'] and proposicao.cd_id:
                        if sync_service.sincronizar_atividades_camara(proposicao):
                            sucessos_camara += 1
                            self.stdout.write(
                                self.style.SUCCESS(f"  ✓ Câmara: OK")
                            )
                        else:
                            erros += 1
                            self.stdout.write(
                                self.style.WARNING(f"  ✗ Câmara: ERRO")
                            )
                    
                    # Log de operação
                    log_database_operation(
                        'SYNC_ACTIVITIES',
                        'Proposicao',
                        proposicao.id,
                        {
                            'identificador': proposicao.identificador_completo,
                            'sf_id': proposicao.sf_id,
                            'cd_id': proposicao.cd_id
                        }
                    )
                    
                except Exception as e:
                    erros += 1
                    error_msg = f"Erro ao processar {proposicao.identificador_completo}: {e}"
                    self.stdout.write(self.style.ERROR(f"  ✗ {error_msg}"))
                    log_error(e, {
                        'command': 'sync_activity_history',
                        'proposicao_id': proposicao.id,
                        'identificador': proposicao.identificador_completo
                    })
                
                # Pausa entre proposições
                if i < total:
                    self.stdout.write("  Aguardando 1 segundo...")
                    time.sleep(1)
            
            # Estatísticas finais
            duration = time.time() - start_time
            self.stdout.write("\n" + "="*50)
            self.stdout.write(self.style.SUCCESS("SINCRONIZAÇÃO CONCLUÍDA"))
            self.stdout.write("="*50)
            self.stdout.write(f"Total de proposições: {total}")
            self.stdout.write(f"Senado (sucessos): {sucessos_senado}")
            self.stdout.write(f"Câmara (sucessos): {sucessos_camara}")
            self.stdout.write(f"Erros: {erros}")
            self.stdout.write(f"Tempo total: {duration:.2f} segundos")
            
            # Log de performance
            log_performance(
                'sync_activity_history',
                duration,
                {
                    'total': total,
                    'sucessos_senado': sucessos_senado,
                    'sucessos_camara': sucessos_camara,
                    'erros': erros
                }
            )
            
        except Exception as e:
            error_msg = f"Erro geral na sincronização: {e}"
            self.stdout.write(self.style.ERROR(error_msg))
            log_error(e, {'command': 'sync_activity_history'})
            raise CommandError(error_msg)
