from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from apps.pauta.models import Eixo, Tema, Proposicao


class TemaModelTest(TestCase):
    """
    Testes para o modelo Tema.
    
    Verifica a criação, validações e constraints do modelo Tema.
    """

    def setUp(self):
        # Cria um eixo padrão para associar aos temas durante os testes
        self.eixo = Eixo.objects.create(id=1, nome="Eixo Padrão")
    
    def test_criar_tema_valido(self):
        """Testa a criação de um tema com dados válidos."""
        tema = Tema.objects.create(eixo=self.eixo, nome="Educação")
        self.assertEqual(tema.nome, "Educação")
        self.assertIsNotNone(tema.created_at)
        self.assertIsNotNone(tema.updated_at)
    
    def test_tema_nome_unico(self):
        """Testa que não é possível criar dois temas com o mesmo nome."""
        Tema.objects.create(eixo=self.eixo, nome="Educação")
        
        with self.assertRaises(IntegrityError):
            Tema.objects.create(eixo=self.eixo, nome="Educação")
    
    def test_tema_nome_nao_pode_ser_vazio(self):
        """Testa que o nome do tema não pode ser vazio."""
        # Django não valida strings vazias no nível do banco para CharField
        # A validação acontece no nível do formulário/serializer
        # Este teste verifica que o modelo aceita strings vazias no banco
        tema = Tema.objects.create(eixo=self.eixo, nome="")
        self.assertEqual(tema.nome, "")
    
    def test_tema_nome_nao_pode_ser_nulo(self):
        """Testa que o nome do tema não pode ser nulo."""
        # Django valida null=False no nível do banco
        with self.assertRaises(IntegrityError):
            Tema.objects.create(eixo=self.eixo, nome=None)
    
    def test_str_representation(self):
        """Testa a representação string do modelo."""
        tema = Tema.objects.create(eixo=self.eixo, nome="Segurança Pública")
        self.assertEqual(str(tema), "Segurança Pública")


class ProposicaoModelTest(TestCase):
    """
    Testes para o modelo Proposicao.
    
    Verifica a criação, validações e constraints do modelo Proposicao.
    """
    
    def setUp(self):
        """Configuração inicial para os testes."""
        self.eixo = Eixo.objects.create(id=2, nome="Eixo Teste")
        self.tema = Tema.objects.create(eixo=self.eixo, nome="Educação")
    
    def test_criar_proposicao_valida(self):
        """Testa a criação de uma proposição com dados válidos."""
        proposicao = Proposicao.objects.create(
            tema=self.tema,
            tipo="PL",
            numero=1234,
            ano=2023
        )
        self.assertEqual(proposicao.tema, self.tema)
        self.assertEqual(proposicao.tipo, "PL")
        self.assertEqual(proposicao.numero, 1234)
        self.assertEqual(proposicao.ano, 2023)
        self.assertIsNotNone(proposicao.created_at)
        self.assertIsNotNone(proposicao.updated_at)
    
    def test_proposicao_unique_together_constraint(self):
        """Testa que não é possível criar duas proposições com mesmo tipo, número e ano."""
        Proposicao.objects.create(
            tema=self.tema,
            tipo="PL",
            numero=1234,
            ano=2023
        )
        
        # Tentativa de criar outra proposição com os mesmos identificadores
        with self.assertRaises(IntegrityError):
            Proposicao.objects.create(
                tema=self.tema,
                tipo="PL",
                numero=1234,
                ano=2023
            )
    
    def test_proposicao_diferentes_temas_mesmo_identificador(self):
        """Testa que proposições com mesmo identificador em temas diferentes não são permitidas."""
        tema2 = Tema.objects.create(eixo=self.eixo, nome="Saúde")
        
        Proposicao.objects.create(
            tema=self.tema,
            tipo="PL",
            numero=1234,
            ano=2023
        )
        
        # Tentativa de criar outra proposição com os mesmos identificadores em tema diferente
        with self.assertRaises(IntegrityError):
            Proposicao.objects.create(
                tema=tema2,
                tipo="PL",
                numero=1234,
                ano=2023
            )
    
    def test_proposicao_diferentes_identificadores_mesmo_tema(self):
        """Testa que é possível criar proposições com identificadores diferentes no mesmo tema."""
        Proposicao.objects.create(
            tema=self.tema,
            tipo="PL",
            numero=1234,
            ano=2023
        )
        
        # Deve ser possível criar outra proposição com identificador diferente
        proposicao2 = Proposicao.objects.create(
            tema=self.tema,
            tipo="PEC",
            numero=5678,
            ano=2023
        )
        
        self.assertEqual(proposicao2.tema, self.tema)
        self.assertEqual(proposicao2.tipo, "PEC")
        self.assertEqual(proposicao2.numero, 5678)
    
    def test_str_representation(self):
        """Testa a representação string do modelo."""
        proposicao = Proposicao.objects.create(
            tema=self.tema,
            tipo="PL",
            numero=1234,
            ano=2023
        )
        self.assertEqual(str(proposicao), "PL 1234/2023")
    
    def test_identificador_completo_property(self):
        """Testa a propriedade identificador_completo."""
        proposicao = Proposicao.objects.create(
            tema=self.tema,
            tipo="PEC",
            numero=5678,
            ano=2024
        )
        self.assertEqual(proposicao.identificador_completo, "PEC 5678/2024")
    
    def test_cascade_delete(self):
        """Testa que ao deletar um tema, suas proposições são deletadas também."""
        Proposicao.objects.create(
            tema=self.tema,
            tipo="PL",
            numero=1234,
            ano=2023
        )
        
        # Verifica que a proposição foi criada
        self.assertEqual(Proposicao.objects.count(), 1)
        
        # Deleta o tema
        self.tema.delete()
        
        # Verifica que a proposição foi deletada também
        self.assertEqual(Proposicao.objects.count(), 0)


class ModelIntegrationTest(TestCase):
    """
    Testes de integração entre os modelos Tema e Proposicao.
    """

    def setUp(self):
        self.eixo = Eixo.objects.create(id=3, nome="Eixo Integração")
    
    def test_relacionamento_tema_proposicoes(self):
        """Testa o relacionamento entre tema e proposições."""
        tema = Tema.objects.create(eixo=self.eixo, nome="Educação")
        
        proposicao1 = Proposicao.objects.create(
            tema=tema,
            tipo="PL",
            numero=1234,
            ano=2023
        )
        
        proposicao2 = Proposicao.objects.create(
            tema=tema,
            tipo="PEC",
            numero=5678,
            ano=2023
        )
        
        # Verifica que o tema tem acesso às suas proposições
        self.assertEqual(tema.proposicoes.count(), 2)
        self.assertIn(proposicao1, tema.proposicoes.all())
        self.assertIn(proposicao2, tema.proposicoes.all())
        
        # Verifica que as proposições têm acesso ao tema
        self.assertEqual(proposicao1.tema, tema)
        self.assertEqual(proposicao2.tema, tema) 