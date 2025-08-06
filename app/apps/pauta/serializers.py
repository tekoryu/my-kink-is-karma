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
                'numero': 2630,
                'ano': 2020
            },
            description='Exemplo de uma proposição válida'
        ),
        OpenApiExample(
            'Criação de proposição',
            value={
                'tema': 1,
                'tipo': 'PL',
                'numero': 2630,
                'ano': 2020
            },
            description='Exemplo para criação de uma nova proposição'
        ),
    ]
)
class ProposicaoSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo Proposicao.
    
    Expõe os campos id, tema, tipo, numero e ano para operações CRUD.
    O campo tema é um PrimaryKeyRelatedField para permitir associação
    direta via ID do tema.
    """
    
    tema = serializers.PrimaryKeyRelatedField(
        queryset=Tema.objects.all(),
        help_text="ID do tema ao qual esta proposição pertence"
    )
    
    class Meta:
        model = Proposicao
        fields = ['id', 'tema', 'tipo', 'numero', 'ano']
        read_only_fields = ['id'] 