from rest_framework import serializers
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample
from .models import Eixo, Tema, Proposicao, SenadoActivityHistory, CamaraActivityHistory


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
    
    Inclui referência ao eixo para operações de escrita. A resposta pode incluir o campo eixo.
    """

    eixo = serializers.PrimaryKeyRelatedField(queryset=Eixo.objects.all(), required=True)
    
    class Meta:
        model = Tema
        fields = ['id', 'nome', 'eixo']
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
            'autor', 'data_apresentacao', 'casa_inicial', 'ementa', 'current_house',
            'ultima_sincronizacao', 'erro_sincronizacao', 'created_at', 'updated_at'
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
            'sf_id', 'cd_id', 'autor', 'data_apresentacao', 'casa_inicial', 'ementa', 'current_house',
            'ultima_sincronizacao', 'erro_sincronizacao',
            'tema_id', 'tema_nome', 'eixo_id', 'eixo_nome',
            'created_at', 'updated_at'
        ]
        read_only_fields = fields


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Atividade do Senado',
            value={
                'id': 1,
                'proposicao': 1,
                'id_informe': 2245882,
                'data': '2025-07-16',
                'descricao': 'Autuado o Projeto de Lei nº 2583/2020, proveniente da Câmara dos Deputados. O projeto vai à publicação.',
                'colegiado_codigo': 1998,
                'colegiado_casa': 'SF',
                'colegiado_sigla': 'PLEN',
                'colegiado_nome': 'Plenário do Senado Federal',
                'ente_administrativo_id': 55312,
                'ente_administrativo_casa': 'SF',
                'ente_administrativo_sigla': 'SLSF',
                'ente_administrativo_nome': 'Secretaria Legislativa do Senado Federal',
                'id_situacao_iniciada': 175,
                'sigla_situacao_iniciada': 'AGDESP',
                'created_at': '2024-01-01T00:00:00Z',
                'updated_at': '2024-01-01T00:00:00Z'
            },
            description='Exemplo de uma atividade do Senado Federal'
        ),
    ]
)
class SenadoActivityHistorySerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo SenadoActivityHistory.
    
    Expõe todos os campos para operações de leitura.
    """
    
    class Meta:
        model = SenadoActivityHistory
        fields = [
            'id', 'proposicao', 'id_informe', 'data', 'descricao',
            'colegiado_codigo', 'colegiado_casa', 'colegiado_sigla', 'colegiado_nome',
            'ente_administrativo_id', 'ente_administrativo_casa', 'ente_administrativo_sigla', 'ente_administrativo_nome',
            'id_situacao_iniciada', 'sigla_situacao_iniciada',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Atividade da Câmara',
            value={
                'id': 1,
                'proposicao': 1,
                'data_hora': '2020-05-12T16:40:00Z',
                'sequencia': 1,
                'sigla_orgao': 'PLEN',
                'uri_orgao': 'https://dadosabertos.camara.leg.br/api/v2/orgaos/180',
                'uri_ultimo_relator': None,
                'regime': 'Urgência (Art. 155, RICD)',
                'descricao_tramitacao': 'Apresentação de Proposição',
                'cod_tipo_tramitacao': '100',
                'descricao_situacao': None,
                'cod_situacao': None,
                'despacho': 'Apresentação do Projeto de Lei n. 2583/2020, pelo Deputado Dr. Luiz Antonio Teixeira Jr. (PP/RJ)',
                'url': 'https://www.camara.leg.br/proposicoesWeb/prop_mostrarintegra?codteor=1892820',
                'ambito': 'Regimental',
                'apreciacao': 'Proposição Sujeita à Apreciação do Plenário',
                'created_at': '2024-01-01T00:00:00Z',
                'updated_at': '2024-01-01T00:00:00Z'
            },
            description='Exemplo de uma atividade da Câmara dos Deputados'
        ),
    ]
)
class CamaraActivityHistorySerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo CamaraActivityHistory.
    
    Expõe todos os campos para operações de leitura.
    """
    
    class Meta:
        model = CamaraActivityHistory
        fields = [
            'id', 'proposicao', 'data_hora', 'sequencia', 'sigla_orgao', 'uri_orgao', 'uri_ultimo_relator',
            'regime', 'descricao_tramitacao', 'cod_tipo_tramitacao', 'descricao_situacao', 'cod_situacao',
            'despacho', 'url', 'ambito', 'apreciacao',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at'] 