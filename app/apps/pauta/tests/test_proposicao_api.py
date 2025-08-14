from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from ..models import Eixo, Tema, Proposicao


class ProposicaoAPITestCase(TestCase):
    """Testes para a API de Proposições."""
    
    def setUp(self):
        """Configuração inicial para os testes."""
        self.client = APIClient()
        self.tema = Tema.objects.create(nome="Tecnologia")
        self.proposicao_data = {
            'tema': self.tema.id,
            'tipo': 'PL',
            'numero': 2630,
            'ano': 2020
        }
        self.url = reverse('pauta:proposicao-list')
    
    def test_criar_proposicao_sucesso(self):
        """Testa a criação bem-sucedida de uma proposição."""
        response = self.client.post(self.url, self.proposicao_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Proposicao.objects.count(), 1)
        
        proposicao = Proposicao.objects.first()
        self.assertEqual(proposicao.tema, self.tema)
        self.assertEqual(proposicao.tipo, 'PL')
        self.assertEqual(proposicao.numero, 2630)
        self.assertEqual(proposicao.ano, 2020)
        
        # Verifica se os dados retornados estão corretos
        self.assertEqual(response.data['tema'], self.tema.id)
        self.assertEqual(response.data['tipo'], 'PL')
        self.assertEqual(response.data['numero'], 2630)
        self.assertEqual(response.data['ano'], 2020)
        self.assertIn('id', response.data)
    
    def test_criar_proposicao_duplicada(self):
        """Testa que não é possível criar uma proposição duplicada."""
        # Cria a primeira proposição
        Proposicao.objects.create(
            tema=self.tema,
            tipo='PL',
            numero=2630,
            ano=2020
        )
        
        # Tenta criar uma proposição com os mesmos dados
        response = self.client.post(self.url, self.proposicao_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Proposicao.objects.count(), 1)  # Apenas a primeira deve existir
        
        # Verifica se a mensagem de erro é apropriada
        self.assertIn('non_field_errors', response.data)
    
    def test_criar_proposicao_tema_inexistente(self):
        """Testa que não é possível criar uma proposição com tema inexistente."""
        data_invalida = self.proposicao_data.copy()
        data_invalida['tema'] = 999  # ID de tema que não existe
        
        response = self.client.post(self.url, data_invalida, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Proposicao.objects.count(), 0)
    
    def test_listar_proposicoes(self):
        """Testa a listagem de proposições."""
        # Cria algumas proposições
        Proposicao.objects.create(
            tema=self.tema,
            tipo='PL',
            numero=2630,
            ano=2020
        )
        Proposicao.objects.create(
            tema=self.tema,
            tipo='PEC',
            numero=123,
            ano=2021
        )
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_obter_proposicao_especifica(self):
        """Testa a obtenção de uma proposição específica."""
        proposicao = Proposicao.objects.create(
            tema=self.tema,
            tipo='PL',
            numero=2630,
            ano=2020
        )
        
        url_detail = reverse('pauta:proposicao-detail', args=[proposicao.id])
        response = self.client.get(url_detail)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], proposicao.id)
        self.assertEqual(response.data['tipo'], 'PL')
        self.assertEqual(response.data['numero'], 2630)
        self.assertEqual(response.data['ano'], 2020)
    
    def test_atualizar_proposicao(self):
        """Testa a atualização de uma proposição."""
        proposicao = Proposicao.objects.create(
            tema=self.tema,
            tipo='PL',
            numero=2630,
            ano=2020
        )
        
        dados_atualizados = {
            'tema': self.tema.id,
            'tipo': 'PEC',
            'numero': 123,
            'ano': 2021
        }
        
        url_detail = reverse('pauta:proposicao-detail', args=[proposicao.id])
        response = self.client.put(url_detail, dados_atualizados, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        proposicao.refresh_from_db()
        self.assertEqual(proposicao.tipo, 'PEC')
        self.assertEqual(proposicao.numero, 123)
        self.assertEqual(proposicao.ano, 2021)
    
    def test_excluir_proposicao(self):
        """Testa a exclusão de uma proposição."""
        proposicao = Proposicao.objects.create(
            tema=self.tema,
            tipo='PL',
            numero=2630,
            ano=2020
        )
        
        url_detail = reverse('pauta:proposicao-detail', args=[proposicao.id])
        response = self.client.delete(url_detail)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Proposicao.objects.count(), 0) 