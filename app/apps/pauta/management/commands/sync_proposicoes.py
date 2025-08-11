from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from apps.pauta.services import APISyncService
import logging
from apps.core.logging_utils import log_performance, log_error, log_database_operation

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Sincroniza proposições com as APIs do Senado Federal e Câmara dos Deputados'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            help='Limite de proposições a processar',
        )
        parser.add_argument(
            '--proposicao-id',
            type=int,
            help='ID específico de uma proposição para sincronizar',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Força a sincronização mesmo para proposições já sincronizadas',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Executa sem salvar alterações no banco de dados',
        )

    def handle(self, *args, **options):
        import time
        start_time = time.time()
        
        from apps.pauta.models import Proposicao
        
        service = APISyncService()
        
        try:
        
            if options['proposicao_id']:
                # Sincronizar proposição específica
                try:
                    proposicao = Proposicao.objects.get(id=options['proposicao_id'])
                    self.stdout.write(f"Sincronizando proposição específica: {proposicao.identificador_completo}")
                    
                    if options['dry_run']:
                        self.stdout.write("Modo dry-run: não serão feitas alterações no banco")
                        # Simular busca sem salvar
                        dados_senado = service.buscar_proposicao_senado(
                            proposicao.tipo, proposicao.numero, proposicao.ano
                        )
                        dados_camara = service.buscar_proposicao_camara(
                            proposicao.tipo, proposicao.numero, proposicao.ano
                        )
                        
                        self.stdout.write(f"Dados Senado: {dados_senado}")
                        self.stdout.write(f"Dados Câmara: {dados_camara}")
                    else:
                        success = service.sincronizar_proposicao(proposicao)
                        if success:
                            self.stdout.write(
                                self.style.SUCCESS(f"Proposição {proposicao.identificador_completo} sincronizada com sucesso")
                            )
                        else:
                            self.stdout.write(
                                self.style.ERROR(f"Erro ao sincronizar proposição {proposicao.identificador_completo}")
                            )
                            
                except Proposicao.DoesNotExist:
                    raise CommandError(f"Proposição com ID {options['proposicao_id']} não encontrada")
            else:
                # Sincronizar todas as proposições
                if options['force']:
                    proposicoes = Proposicao.objects.all()
                    self.stdout.write("Modo force: sincronizando todas as proposições")
                else:
                    proposicoes = Proposicao.objects.filter(ultima_sincronizacao__isnull=True)
                    self.stdout.write("Sincronizando apenas proposições não sincronizadas")
            
            total = proposicoes.count()
            self.stdout.write(f"Total de proposições a processar: {total}")
            
            if total == 0:
                self.stdout.write(self.style.WARNING("Nenhuma proposição para sincronizar"))
                return
            
            if options['dry_run']:
                self.stdout.write("Modo dry-run: não serão feitas alterações no banco")
                # Mostrar apenas estatísticas
                limit = options['limit'] or 5
                proposicoes_amostra = proposicoes[:limit]
                self.stdout.write(f"Mostrando amostra de {limit} proposições:")
                
                for proposicao in proposicoes_amostra:
                    self.stdout.write(f"- {proposicao.identificador_completo}")
            else:
                # Executar sincronização real
                with transaction.atomic():
                    stats = service.sincronizar_todas_proposicoes(limit=options['limit'])
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Sincronização concluída: {stats['sucessos']} sucessos, {stats['erros']} erros"
                        )
                    )
                    
                    if stats['erros'] > 0:
                        self.stdout.write(
                            self.style.WARNING(
                                f"Verifique os logs para detalhes dos {stats['erros']} erros"
                            )
                        )
            
            # Log performance metrics
            duration = time.time() - start_time
            log_performance('sync_proposicoes_command', duration, {
                'total_processed': total,
                'force': options['force'],
                'dry_run': options['dry_run'],
                'limit': options['limit']
            })
            
        except Exception as e:
            log_error(e, {
                'command': 'sync_proposicoes',
                'options': options
            })
            raise
