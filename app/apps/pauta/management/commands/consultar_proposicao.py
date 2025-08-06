import logging
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from apps.pauta.models import Proposicao
from apps.pauta.services import consultar_e_salvar_dados_iniciais

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Consulta dados iniciais de uma proposição específica na API SF'

    def add_arguments(self, parser):
        parser.add_argument(
            'sigla',
            type=str,
            help='Sigla da proposição (ex: PL, PEC, MPV)'
        )
        parser.add_argument(
            'numero',
            type=int,
            help='Número da proposição'
        )
        parser.add_argument(
            'ano',
            type=int,
            help='Ano da proposição'
        )

        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Executa sem salvar mudanças no banco de dados'
        )

    def handle(self, *args, **options):
        sigla = options['sigla']
        numero = options['numero']
        ano = options['ano']
        dry_run = options['dry_run']
        
        self.stdout.write(
            self.style.SUCCESS(f'Consultando dados para {sigla} {numero}/{ano}...')
        )
        
        try:
            # Buscar a proposição
            proposicao = self._get_proposicao(sigla, numero, ano)
            
            self.stdout.write(f'Proposição: {proposicao.identificador_completo}')
            self.stdout.write(f'Tema: {proposicao.tema.nome}')
            
            # Consultar dados na API
            dados = consultar_e_salvar_dados_iniciais(proposicao)
            
            if dados is None:
                self.stdout.write(
                    self.style.ERROR(f'Falha ao consultar dados para {proposicao.identificador_completo}')
                )
                return
            
            # Exibir resumo dos dados
            self.stdout.write(
                self.style.SUCCESS(f'Dados consultados com sucesso para {proposicao.identificador_completo}')
            )
            
            # Mostrar informações principais dos dados
            self._exibir_resumo_dados(dados)
            
            if dry_run:
                self.stdout.write(
                    self.style.WARNING('MODO DRY-RUN: Nenhuma mudança foi salva no banco de dados')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS('Dados salvos no histórico de atualização')
                )
                
        except Exception as e:
            logger.error(f'Erro ao processar {sigla} {numero}/{ano}: {e}')
            self.stdout.write(
                self.style.ERROR(f'Erro ao processar {sigla} {numero}/{ano}: {e}')
            )
            raise CommandError(str(e))

    def _get_proposicao(self, sigla, numero, ano):
        """
        Busca uma proposição existente.
        """
        try:
            proposicao = Proposicao.objects.get(
                tipo=sigla,
                numero=numero,
                ano=ano
            )
            return proposicao
            
        except Proposicao.DoesNotExist:
            raise CommandError(
                f'Proposição {sigla} {numero}/{ano} não encontrada no banco de dados'
            )

    def _exibir_resumo_dados(self, dados):
        """
        Exibe um resumo dos dados retornados pela API.
        """
        self.stdout.write('\n' + '='*50)
        self.stdout.write('RESUMO DOS DADOS')
        self.stdout.write('='*50)
        
        # Verificar se dados é uma string (XML) ou dict (JSON)
        if isinstance(dados, str):
            self.stdout.write("Dados retornados em formato XML/string")
            self.stdout.write(f"Tamanho da resposta: {len(dados)} caracteres")
            self.stdout.write("Primeiros 200 caracteres:")
            self.stdout.write(dados[:200] + "...")
            return
        
        # Verificar se dados é uma lista
        if isinstance(dados, list):
            if len(dados) > 0:
                dados = dados[0]  # Pegar primeiro item
            else:
                self.stdout.write("Lista vazia retornada")
                return
        
        # Verificar se dados é um dicionário
        if not isinstance(dados, dict):
            self.stdout.write(f"Formato de dados inesperado: {type(dados)}")
            self.stdout.write(f"Conteúdo: {str(dados)[:200]}...")
            return
        
        # Informações básicas
        if 'identificacao' in dados:
            ident = dados['identificacao']
            if isinstance(ident, dict):
                self.stdout.write(f"ID do Processo: {ident.get('id', 'N/A')}")
                self.stdout.write(f"Identificação: {ident.get('identificacao', 'N/A')}")
            else:
                self.stdout.write(f"Identificação: {ident}")
        
        # Ementa
        if 'ementa' in dados:
            ementa = dados['ementa']
            if isinstance(ementa, dict):
                texto = ementa.get('texto', 'N/A')
                self.stdout.write(f"Ementa: {texto[:100]}...")
            else:
                self.stdout.write(f"Ementa: {str(ementa)[:100]}...")
        
        # Situação
        if 'situacao' in dados:
            situacao = dados['situacao']
            if isinstance(situacao, dict):
                self.stdout.write(f"Situação: {situacao.get('descricao', 'N/A')}")
            else:
                self.stdout.write(f"Situação: {situacao}")
        
        # Autoria
        if 'autoria' in dados and dados['autoria']:
            autores = dados['autoria']
            if isinstance(autores, list) and len(autores) > 0:
                primeiro_autor = autores[0]
                if isinstance(primeiro_autor, dict):
                    self.stdout.write(f"Primeiro Autor: {primeiro_autor.get('nome', 'N/A')}")
                else:
                    self.stdout.write(f"Primeiro Autor: {primeiro_autor}")
        
        # Data de apresentação
        if 'apresentacao' in dados:
            apresentacao = dados['apresentacao']
            if isinstance(apresentacao, dict):
                self.stdout.write(f"Data de Apresentação: {apresentacao.get('data', 'N/A')}")
            else:
                self.stdout.write(f"Data de Apresentação: {apresentacao}")
        
        self.stdout.write('='*50) 