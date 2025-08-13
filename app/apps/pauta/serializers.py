from rest_framework import serializers
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample
from .models import Eixo, Tema, Proposicao


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
                'cd_id': 2386490,
                'autor': 'Deputado João Silva',
                'data_apresentacao': '2023-01-15',
                'casa_inicial': 'CD',
                'ultima_sincronizacao': '2024-01-01T10:00:00Z',
                'erro_sincronizacao': None,
                'created_at': '2024-01-01T00:00:00Z',
                'updated_at': '2024-01-01T10:00:00Z'
            },
            description='Exemplo de uma proposição válida com todos os campos'
        ),
        OpenApiExample(
            'Criação de proposição',
            value={
                'tema': 1,
                'tipo': 'PL',
                'numero': 4381,
                'ano': 2023,
                'sf_id': None,
                'cd_id': None,
                'autor': None,
                'data_apresentacao': None,
                'casa_inicial': None,
                'ultima_sincronizacao': None,
                'erro_sincronizacao': None
            },
            description='Exemplo para criação de uma nova proposição'
        ),
    ]
)
class ProposicaoSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo Proposicao.
    
    Expõe todos os campos para operações CRUD.
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
            'id', 'tema', 'tipo', 'numero', 'ano', 'sf_id', 'cd_id',
            'autor', 'data_apresentacao', 'casa_inicial', 'ultima_sincronizacao',
            'erro_sincronizacao', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at'] 


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Eixo com temas',
            value={
                'id': 1,
                'nome': 'Desenvolvimento Econômico',
                'created_at': '2024-01-01T00:00:00Z',
                'updated_at': '2024-01-01T00:00:00Z',
                'temas_count': 5
            },
            description='Exemplo de um eixo com contagem de temas'
        ),
    ]
)
class EixoReadOnlySerializer(serializers.ModelSerializer):
    """
    Serializer read-only para o modelo Eixo com contagem de temas.
    """
    
    temas_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Eixo
        fields = ['id', 'nome', 'created_at', 'updated_at', 'temas_count']
        read_only_fields = fields
    
    def get_temas_count(self, obj):
        return obj.temas.count()


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Tema com eixo e proposições',
            value={
                'id': 1,
                'nome': 'Tecnologia',
                'eixo_id': 1,
                'eixo_nome': 'Desenvolvimento Econômico',
                'proposicoes_count': 10,
                'created_at': '2024-01-01T00:00:00Z',
                'updated_at': '2024-01-01T00:00:00Z'
            },
            description='Exemplo de um tema com dados do eixo e contagem de proposições'
        ),
    ]
)
class TemaReadOnlySerializer(serializers.ModelSerializer):
    """
    Serializer read-only para o modelo Tema com dados do eixo e contagem de proposições.
    """
    
    eixo_id = serializers.IntegerField(source='eixo.id')
    eixo_nome = serializers.CharField(source='eixo.nome')
    proposicoes_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Tema
        fields = ['id', 'nome', 'eixo_id', 'eixo_nome', 'proposicoes_count', 'created_at', 'updated_at']
        read_only_fields = fields
    
    def get_proposicoes_count(self, obj):
        return obj.proposicoes.count()


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Proposição completa',
            value={
                'id': 1,
                'tipo': 'PL',
                'numero': 4381,
                'ano': 2023,
                'identificador_completo': 'PL 4381/2023',
                'tema_id': 1,
                'tema_nome': 'Tecnologia',
                'eixo_id': 1,
                'eixo_nome': 'Desenvolvimento Econômico',
                'created_at': '2024-01-01T00:00:00Z',
                'updated_at': '2024-01-01T00:00:00Z'
            },
            description='Exemplo de uma proposição com dados completos do tema e eixo'
        ),
    ]
)
class ProposicaoReadOnlySerializer(serializers.ModelSerializer):
    """
    Serializer read-only para o modelo Proposicao com dados completos do tema e eixo.
    """
    
    identificador_completo = serializers.CharField()
    tema_id = serializers.IntegerField(source='tema.id')
    tema_nome = serializers.CharField(source='tema.nome')
    eixo_id = serializers.IntegerField(source='tema.eixo.id')
    eixo_nome = serializers.CharField(source='tema.eixo.nome')
    
    class Meta:
        model = Proposicao
        fields = [
            'id', 'tipo', 'numero', 'ano', 'identificador_completo',
            'tema_id', 'tema_nome', 'eixo_id', 'eixo_nome',
            'created_at', 'updated_at'
        ]
        read_only_fields = fields 