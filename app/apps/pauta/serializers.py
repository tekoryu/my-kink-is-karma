from rest_framework import serializers
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample
from .models import Tema, Proposicao


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Tema válido',
            value={
                'id': 1,
                'nome': 'Tecnologia'
            },
            description='Exemplo de um tema válido'
        ),
        OpenApiExample(
            'Criação de tema',
            value={
                'nome': 'Novo Tema'
            },
            description='Exemplo para criação de um novo tema'
        ),
    ]
)
class TemaSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo Tema.
    
    Expõe os campos id e nome para operações CRUD.
    """
    
    class Meta:
        model = Tema
        fields = ['id', 'nome']
        read_only_fields = ['id']


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Proposição válida',
            value={
                'id': 1,
                'tema': 1,
                'tipo': 'PL',
                'numero': 4381,
                'ano': 2023,
                'sf_id': 8797561,
                'sf_codigo_materia': 167384,
                'papel_sf': 'Revisora',
                'tipo_conteudo': 'Norma Geral',
                'ementa': 'Estabelece medidas a serem adotadas pelas delegacias de polícia...',
                'tipo_documento': 'Projeto de Lei Ordinária',
                'sf_data_apresentacao': '2025-02-26',
                'sf_autoria': 'Câmara dos Deputados',
                'sf_tramitando': 'Sim',
                'sf_last_info': 'EVENTO_LEGISLATIVO',
                'sf_lastupdate_date': '2025-07-03T16:39:41.242'
            },
            description='Exemplo de uma proposição válida com dados da API do Senado Federal'
        ),
        OpenApiExample(
            'Criação de proposição',
            value={
                'tema': 1,
                'tipo': 'PL',
                'numero': 4381,
                'ano': 2023
            },
            description='Exemplo para criação de uma nova proposição (campos obrigatórios)'
        ),
    ]
)
class ProposicaoSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo Proposicao.
    
    Expõe os campos básicos e os dados da API do Senado Federal para operações CRUD.
    O campo tema é um PrimaryKeyRelatedField para permitir associação
    direta via ID do tema.
    """
    
    tema = serializers.PrimaryKeyRelatedField(
        queryset=Tema.objects.all(),
        help_text="ID do tema ao qual esta proposição pertence"
    )
    
    class Meta:
        model = Proposicao
        fields = [
            'id', 'tema', 'tipo', 'numero', 'ano',
            'sf_id', 'sf_codigo_materia', 'papel_sf', 'tipo_conteudo',
            'ementa', 'tipo_documento', 'sf_data_apresentacao', 'sf_autoria',
            'sf_tramitando', 'sf_last_info', 'sf_lastupdate_date'
        ]
        read_only_fields = ['id'] 