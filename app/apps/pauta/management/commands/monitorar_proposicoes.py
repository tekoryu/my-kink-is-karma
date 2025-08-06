import json
import logging
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.pauta.models import Proposicao, HistoricoAtualizacao
from apps.pauta.services import consultar_api_proposicao

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Monitora proposições ativas e atualiza histórico de mudanças'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Executa sem salvar mudanças no banco de dados',
        )
        parser.add_argument(
            '--proposicao-id',
            type=int,
            help='Monitora apenas uma proposição específica por ID',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        proposicao_id = options.get('proposicao_id')
        
        self.stdout.write(
            self.style.SUCCESS('Iniciando monitoramento de proposições...')
        )
        
        # Filtra proposições ativas
        if proposicao_id:
            proposicoes = Proposicao.objects.filter(id=proposicao_id)
            if not proposicoes.exists():
                self.stdout.write(
                    self.style.ERROR(f'Proposição com ID {proposicao_id} não encontrada')
                )
                return
        else:
            proposicoes = Proposicao.objects.all()
        
        total_proposicoes = proposicoes.count()
        self.stdout.write(f'Encontradas {total_proposicoes} proposições para monitorar')
        
        atualizadas = 0
        erros = 0
        
        for proposicao in proposicoes:
            try:
                self.stdout.write(f'Monitorando: {proposicao.identificador_completo}')
                
                # Consulta API externa
                dados_api = consultar_api_proposicao(proposicao)
                
                if dados_api is None:
                    self.stdout.write(
                        self.style.WARNING(f'Falha ao consultar API para {proposicao.identificador_completo}')
                    )
                    erros += 1
                    continue
                
                # Obtém último histórico
                ultimo_historico = proposicao.historicos_atualizacao.first()
                
                # Verifica se houve mudanças
                if self._houve_mudancas(ultimo_historico, dados_api):
                    if not dry_run:
                        with transaction.atomic():
                            HistoricoAtualizacao.objects.create(
                                proposicao=proposicao,
                                dados_atualizados=dados_api
                            )
                    
                    self.stdout.write(
                        self.style.SUCCESS(f'Mudança detectada em {proposicao.identificador_completo}')
                    )
                    atualizadas += 1
                else:
                    self.stdout.write(f'Sem mudanças em {proposicao.identificador_completo}')
                    
            except Exception as e:
                logger.error(f'Erro ao processar {proposicao.identificador_completo}: {e}')
                self.stdout.write(
                    self.style.ERROR(f'Erro ao processar {proposicao.identificador_completo}: {e}')
                )
                erros += 1
        
        # Resumo final
        self.stdout.write('\n' + '='*50)
        self.stdout.write('RESUMO DO MONITORAMENTO')
        self.stdout.write('='*50)
        self.stdout.write(f'Total de proposições: {total_proposicoes}')
        self.stdout.write(f'Atualizadas: {atualizadas}')
        self.stdout.write(f'Erros: {erros}')
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('MODO DRY-RUN: Nenhuma mudança foi salva no banco de dados')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('Monitoramento concluído com sucesso!')
            )

    def _houve_mudancas(self, ultimo_historico, dados_api):
        """
        Compara os dados da API com o último histórico para detectar mudanças.
        
        Args:
            ultimo_historico: Último registro de HistoricoAtualizacao ou None
            dados_api: Dados retornados pela API
            
        Returns:
            bool: True se houve mudanças, False caso contrário
        """
        if ultimo_historico is None:
            # Primeira atualização
            return True
        
        dados_anteriores = ultimo_historico.dados_atualizados
        
        # Compara campos relevantes para detectar mudanças
        campos_importantes = ['status', 'situacao', 'comissoes', 'ultima_atualizacao']
        
        for campo in campos_importantes:
            if campo in dados_api and campo in dados_anteriores:
                if dados_api[campo] != dados_anteriores[campo]:
                    logger.info(f'Mudança detectada no campo {campo}')
                    return True
        
        return False 