from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from apps.pauta.models import Eixo, Tema


class TemaAPITestCase(TestCase):
    """
    Testes para a API de Temas.
    
    Testa as operações CRUD básicas e validações.
    """
    
    def setUp(self):
        """Configuração inicial para os testes."""
        self.client = APIClient()
        self.temas_url = reverse('pauta:tema-list')

        # Cria um eixo padrão e inclui nos payloads
        self.eixo = Eixo.objects.create(id=10, nome='Eixo API')
        
        # Dados de teste
        self.tema_data = {
            'nome': 'Educação',
            'eixo': self.eixo.id,
        }
        
        self.tema_data_2 = {
            'nome': 'Segurança Pública',
            'eixo': self.eixo.id,
        }
    
    def test_criar_tema_sucesso(self):
        """
        Testa a criação de um tema com dados válidos.
        
        Deve retornar status 201 e criar o tema no banco.
        """
        response = self.client.post(self.temas_url, self.tema_data, format='json')
        
        # Verifica o status da resposta
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verifica se o tema foi criado no banco
        self.assertEqual(Tema.objects.count(), 1)
        
        # Verifica os dados retornados
        tema = Tema.objects.first()
        self.assertEqual(tema.nome, self.tema_data['nome'])
        self.assertEqual(response.data['id'], tema.id)
        self.assertEqual(response.data['nome'], tema.nome)
    
    def test_criar_tema_nome_duplicado(self):
        """
        Testa a criação de um tema com nome duplicado.
        
        Deve retornar status 400 e não criar o tema.
        """
        # Cria o primeiro tema
        Tema.objects.create(eixo=self.eixo, nome=self.tema_data['nome'])
        
        # Tenta criar um tema com o mesmo nome
        response = self.client.post(self.temas_url, self.tema_data, format='json')
        
        # Verifica o status da resposta
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Verifica se não foi criado um novo tema
        self.assertEqual(Tema.objects.count(), 1)
        
        # Verifica se a mensagem de erro contém informação sobre duplicação
        self.assertIn('nome', response.data)
    
    def test_criar_tema_nome_vazio(self):
        """
        Testa a criação de um tema com nome vazio.
        
        Deve retornar status 400 e não criar o tema.
        """
        tema_data_invalido = {'nome': ''}
        response = self.client.post(self.temas_url, tema_data_invalido, format='json')
        
        # Verifica o status da resposta
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Verifica se não foi criado um tema
        self.assertEqual(Tema.objects.count(), 0)
    
    def test_criar_tema_sem_nome(self):
        """
        Testa a criação de um tema sem fornecer o nome.
        
        Deve retornar status 400 e não criar o tema.
        """
        response = self.client.post(self.temas_url, {}, format='json')
        
        # Verifica o status da resposta
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Verifica se não foi criado um tema
        self.assertEqual(Tema.objects.count(), 0)
    
    def test_listar_temas_vazio(self):
        """
        Testa a listagem de temas quando não há temas cadastrados.
        
        Deve retornar status 200 e uma lista vazia.
        """
        response = self.client.get(self.temas_url)
        
        # Verifica o status da resposta
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verifica se retorna uma lista vazia
        self.assertEqual(response.data, [])
    
    def test_listar_temas_com_dados(self):
        """
        Testa a listagem de temas quando há temas cadastrados.
        
        Deve retornar status 200 e a lista de temas.
        """
        # Cria alguns temas
        tema1 = Tema.objects.create(eixo=self.eixo, nome=self.tema_data['nome'])
        tema2 = Tema.objects.create(eixo=self.eixo, nome=self.tema_data_2['nome'])
        
        response = self.client.get(self.temas_url)
        
        # Verifica o status da resposta
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verifica se retorna a lista de temas
        self.assertEqual(len(response.data), 2)
        
        # Verifica se os dados estão corretos
        nomes_retornados = [tema['nome'] for tema in response.data]
        self.assertIn(tema1.nome, nomes_retornados)
        self.assertIn(tema2.nome, nomes_retornados)
    
    def test_obter_tema_especifico(self):
        """
        Testa a obtenção de um tema específico por ID.
        
        Deve retornar status 200 e os dados do tema.
        """
        tema = Tema.objects.create(eixo=self.eixo, nome=self.tema_data['nome'])
        url = reverse('pauta:tema-detail', args=[tema.id])
        
        response = self.client.get(url)
        
        # Verifica o status da resposta
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verifica os dados retornados
        self.assertEqual(response.data['id'], tema.id)
        self.assertEqual(response.data['nome'], tema.nome)
    
    def test_obter_tema_inexistente(self):
        """
        Testa a obtenção de um tema que não existe.
        
        Deve retornar status 404.
        """
        url = reverse('pauta:tema-detail', args=[999])
        
        response = self.client.get(url)
        
        # Verifica o status da resposta
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_atualizar_tema(self):
        """
        Testa a atualização de um tema existente.
        
        Deve retornar status 200 e atualizar o tema.
        """
        tema = Tema.objects.create(eixo=self.eixo, nome=self.tema_data['nome'])
        url = reverse('pauta:tema-detail', args=[tema.id])
        
        dados_atualizados = {'nome': 'Saúde Pública', 'eixo': self.eixo.id}
        response = self.client.put(url, dados_atualizados, format='json')
        
        # Verifica o status da resposta
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verifica se o tema foi atualizado
        tema.refresh_from_db()
        self.assertEqual(tema.nome, dados_atualizados['nome'])
        self.assertEqual(response.data['nome'], dados_atualizados['nome'])
    
    def test_deletar_tema(self):
        """
        Testa a exclusão de um tema.
        
        Deve retornar status 204 e remover o tema do banco.
        """
        tema = Tema.objects.create(eixo=self.eixo, nome=self.tema_data['nome'])
        url = reverse('pauta:tema-detail', args=[tema.id])
        
        response = self.client.delete(url)
        
        # Verifica o status da resposta
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verifica se o tema foi removido
        self.assertEqual(Tema.objects.count(), 0) 