from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from apps.pauta.services_impl.data_processing_service import DataProcessingService
import logging
from apps.core.logging_utils import log_performance, log_error, log_database_operation

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Verifica e atualiza o campo current_house para todas as proposições baseado no histórico de atividades'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            help='Limite de proposições a processar',
        )
        parser.add_argument(
            '--proposicao-id',
            type=int,
            help='ID específico de uma proposição para verificar',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Executa sem salvar alterações no banco de dados',
        )
        parser.add_argument(
            '--show-details',
            action='store_true',
            help='Mostra detalhes das alterações realizadas',
        )

    def handle(self, *args, **options):
        import time
        start_time = time.time()
        
        from apps.pauta.models import Proposicao
        
        service = DataProcessingService()
        total_processed = 0
        updates_made = 0
        
        try:
            if options['proposicao_id']:
                # Verificar proposição específica
                try:
                    proposicao = Proposicao.objects.get(id=options['proposicao_id'])
                    self.stdout.write(f"Verificando proposição específica: {proposicao.identificador_completo}")
                    
                    current_house_before = proposicao.current_house
                    
                    if options['dry_run']:
                        self.stdout.write("Modo dry-run: não serão feitas alterações no banco")
                        # Simular processamento sem salvar
                        self._show_proposicao_status(proposicao)
                    else:
                        success = service.update_derived_fields(proposicao)
                        
                        proposicao.refresh_from_db()
                        current_house_after = proposicao.current_house
                        
                        if success:
                            total_processed = 1
                            if current_house_before != current_house_after:
                                updates_made = 1
                                self.stdout.write(
                                    self.style.SUCCESS(
                                        f"Proposição {proposicao.identificador_completo}: "
                                        f"current_house atualizado de '{current_house_before}' para '{current_house_after}'"
                                    )
                                )
                            else:
                                self.stdout.write(
                                    f"Proposição {proposicao.identificador_completo}: "
                                    f"current_house mantido como '{current_house_after}'"
                                )
                                
                            if options['show_details']:
                                self._show_proposicao_status(proposicao)
                        else:
                            self.stdout.write(
                                self.style.ERROR(f"Erro ao processar proposição {proposicao.identificador_completo}")
                            )
                            
                except Proposicao.DoesNotExist:
                    raise CommandError(f"Proposição com ID {options['proposicao_id']} não encontrada")
            else:
                # Verificar todas as proposições
                queryset = Proposicao.objects.all().order_by('id')
                
                if options['limit']:
                    queryset = queryset[:options['limit']]
                
                total_count = queryset.count()
                self.stdout.write(f"Total de proposições a processar: {total_count}")
                
                if total_count == 0:
                    self.stdout.write(self.style.WARNING("Nenhuma proposição encontrada"))
                    return
                
                if options['dry_run']:
                    self.stdout.write("Modo dry-run: não serão feitas alterações no banco")
                    limit_show = min(5, total_count)
                    self.stdout.write(f"Mostrando status de {limit_show} proposições:")
                    
                    for proposicao in queryset[:limit_show]:
                        self._show_proposicao_status(proposicao)
                else:
                    # Processar proposições
                    self.stdout.write("Processando proposições...")
                    
                    for i, proposicao in enumerate(queryset, 1):
                        current_house_before = proposicao.current_house
                        
                        success = service.update_derived_fields(proposicao)
                        
                        if success:
                            total_processed += 1
                            proposicao.refresh_from_db()
                            current_house_after = proposicao.current_house
                            
                            if current_house_before != current_house_after:
                                updates_made += 1
                                
                                if options['show_details']:
                                    self.stdout.write(
                                        self.style.SUCCESS(
                                            f"[{i}/{total_count}] {proposicao.identificador_completo}: "
                                            f"current_house: '{current_house_before}' → '{current_house_after}'"
                                        )
                                    )
                            elif options['show_details']:
                                self.stdout.write(
                                    f"[{i}/{total_count}] {proposicao.identificador_completo}: "
                                    f"current_house mantido: '{current_house_after}'"
                                )
                        else:
                            if options['show_details']:
                                self.stdout.write(
                                    self.style.ERROR(
                                        f"[{i}/{total_count}] Erro ao processar {proposicao.identificador_completo}"
                                    )
                                )
                        
                        # Progress indicator for large batches
                        if i % 100 == 0:
                            self.stdout.write(f"Processadas {i}/{total_count} proposições...")
                    
                    # Summary with additional context
                    from apps.pauta.models import SenadoActivityHistory, CamaraActivityHistory
                    props_with_activities = 0
                    props_without_activities = 0
                    
                    for prop in queryset:
                        sf_count = SenadoActivityHistory.objects.filter(proposicao=prop).count()
                        cd_count = CamaraActivityHistory.objects.filter(proposicao=prop).count()
                        
                        if sf_count > 0 or cd_count > 0:
                            props_with_activities += 1
                        else:
                            props_without_activities += 1
                    
                    self.stdout.write("\n" + "="*60)
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Processamento concluído:\n"
                            f"  - Total processadas: {total_processed}\n"
                            f"  - Atualizações realizadas: {updates_made}\n"
                            f"  - Sem alteração: {total_processed - updates_made}\n"
                            f"  - Com atividades: {props_with_activities}\n"
                            f"  - Sem atividades: {props_without_activities}"
                        )
                    )
                    
                    if updates_made == 0:
                        self.stdout.write(
                            self.style.SUCCESS("✅ Todos os campos current_house estão corretos!")
                        )
                        
                    if props_without_activities > 0:
                        self.stdout.write(
                            f"\nℹ️  {props_without_activities} proposições têm current_house=None porque não possuem histórico de atividades.\n"
                            f"   Isso é o comportamento esperado - current_house só é definido quando há atividades registradas."
                        )
            
            # Log performance metrics
            duration = time.time() - start_time
            log_performance('check_current_house_command', duration, {
                'total_processed': total_processed,
                'updates_made': updates_made,
                'dry_run': options['dry_run'],
                'limit': options['limit'],
                'single_proposicao': bool(options['proposicao_id'])
            })
            
        except Exception as e:
            log_error(e, {
                'command': 'check_current_house',
                'options': options
            })
            raise

    def _show_proposicao_status(self, proposicao):
        """Mostra o status atual da proposição e suas atividades."""
        from apps.pauta.models import SenadoActivityHistory, CamaraActivityHistory
        from django.db.models import Max, Count
        
        # Contar atividades
        senado_count = SenadoActivityHistory.objects.filter(proposicao=proposicao).count()
        camara_count = CamaraActivityHistory.objects.filter(proposicao=proposicao).count()
        
        # Última atividade de cada casa
        ultima_senado = None
        ultima_camara = None
        
        if senado_count > 0:
            ultima_senado = (
                SenadoActivityHistory.objects
                .filter(proposicao=proposicao)
                .aggregate(ultima=Max('data'))
                .get('ultima')
            )
            
        if camara_count > 0:
            ultima_camara = (
                CamaraActivityHistory.objects
                .filter(proposicao=proposicao)
                .aggregate(ultima=Max('data_hora'))
                .get('ultima')
            )
            # Convert datetime to date for display
            if ultima_camara:
                ultima_camara = ultima_camara.date()
        
        self.stdout.write(f"\n{proposicao.identificador_completo}:")
        self.stdout.write(f"  - current_house atual: {proposicao.current_house}")
        self.stdout.write(f"  - Atividades Senado: {senado_count} (última: {ultima_senado})")
        self.stdout.write(f"  - Atividades Câmara: {camara_count} (última: {ultima_camara})")
        
        # Determinar qual deveria ser o current_house
        expected_house = None
        if ultima_senado and ultima_camara:
            expected_house = 'CD' if ultima_camara > ultima_senado else 'SF'
        elif ultima_camara:
            expected_house = 'CD'
        elif ultima_senado:
            expected_house = 'SF'
        
        if expected_house:
            if proposicao.current_house == expected_house:
                self.stdout.write(f"  - Status: ✓ Correto (deveria ser {expected_house})")
            else:
                self.stdout.write(f"  - Status: ⚠ Necessita atualização (deveria ser {expected_house})")
        else:
            self.stdout.write(f"  - Status: ⚠ Sem atividades registradas")
