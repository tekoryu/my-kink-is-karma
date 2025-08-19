import logging
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from .models import Eixo, Tema, Proposicao, SenadoActivityHistory, CamaraActivityHistory
from .serializers import (
    TemaSerializer, ProposicaoSerializer,
    EixoReadOnlySerializer, TemaReadOnlySerializer, ProposicaoReadOnlySerializer,
    SenadoActivityHistorySerializer, CamaraActivityHistorySerializer
)
from apps.core.logging_utils import log_database_operation, log_error, log_performance


@extend_schema_view(
    list=extend_schema(
        summary="Listar temas",
        description="Retorna uma lista de todos os temas disponíveis",
        tags=["temas"],
        responses={200: TemaSerializer(many=True)},
    ),
    create=extend_schema(
        summary="Criar tema",
        description="Cria um novo tema",
        tags=["temas"],
        request=TemaSerializer,
        responses={201: TemaSerializer},
    ),
    retrieve=extend_schema(
        summary="Obter tema",
        description="Retorna detalhes de um tema específico",
        tags=["temas"],
        responses={200: TemaSerializer},
    ),
    update=extend_schema(
        summary="Atualizar tema",
        description="Atualiza completamente um tema existente",
        tags=["temas"],
        request=TemaSerializer,
        responses={200: TemaSerializer},
    ),
    partial_update=extend_schema(
        summary="Atualizar tema parcialmente",
        description="Atualiza parcialmente um tema existente",
        tags=["temas"],
        request=TemaSerializer,
        responses={200: TemaSerializer},
    ),
    destroy=extend_schema(
        summary="Excluir tema",
        description="Remove um tema existente",
        tags=["temas"],
        responses={204: None},
    ),
)
class TemaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para o modelo Tema.
    
    Fornece as ações CRUD padrão:
    - list: GET /api/temas/
    - create: POST /api/temas/
    - retrieve: GET /api/temas/{id}/
    - update: PUT /api/temas/{id}/
    - partial_update: PATCH /api/temas/{id}/
    - destroy: DELETE /api/temas/{id}/
    """
    
    queryset = Tema.objects.all()
    serializer_class = TemaSerializer
    permission_classes = [AllowAny]  # Allow all operations for now
    pagination_class = None  # Disable pagination for now
    
    def list(self, request, *args, **kwargs):
        """Override list method to add logging"""
        try:
            import time
            start_time = time.time()
            
            response = super().list(request, *args, **kwargs)
            
            duration = time.time() - start_time
            log_performance('tema_list', duration, {'count': len(response.data)})
            log_database_operation('SELECT', 'Tema', details=f'Retrieved {len(response.data)} temas')
            
            return response
        except Exception as e:
            log_error(e, {'view': 'TemaViewSet', 'action': 'list'})
            raise
    
    def create(self, request, *args, **kwargs):
        """Override create method to add logging"""
        try:
            response = super().create(request, *args, **kwargs)
            log_database_operation('INSERT', 'Tema', response.data.get('id'), 
                                 {'nome': response.data.get('nome')})
            return response
        except Exception as e:
            log_error(e, {'view': 'TemaViewSet', 'action': 'create', 'data': request.data})
            raise
    
    def update(self, request, *args, **kwargs):
        """Override update method to add logging"""
        try:
            response = super().update(request, *args, **kwargs)
            log_database_operation('UPDATE', 'Tema', response.data.get('id'), 
                                 {'nome': response.data.get('nome')})
            return response
        except Exception as e:
            log_error(e, {'view': 'TemaViewSet', 'action': 'update', 'data': request.data})
            raise
    
    def destroy(self, request, *args, **kwargs):
        """Override destroy method to add logging"""
        try:
            instance = self.get_object()
            instance_id = instance.id
            instance_name = instance.nome
            
            response = super().destroy(request, *args, **kwargs)
            log_database_operation('DELETE', 'Tema', instance_id, {'nome': instance_name})
            return response
        except Exception as e:
            log_error(e, {'view': 'TemaViewSet', 'action': 'destroy'})
            raise


@extend_schema_view(
    list=extend_schema(
        summary="Listar proposições",
        description="Retorna uma lista de todas as proposições cadastradas",
        tags=["proposições"],
        responses={200: ProposicaoSerializer(many=True)},
    ),
    create=extend_schema(
        summary="Criar proposição",
        description="Cria uma nova proposição",
        tags=["proposições"],
        request=ProposicaoSerializer,
        responses={201: ProposicaoSerializer},
    ),
    retrieve=extend_schema(
        summary="Obter proposição",
        description="Retorna detalhes de uma proposição específica",
        tags=["proposições"],
        responses={200: ProposicaoSerializer},
    ),
    update=extend_schema(
        summary="Atualizar proposição",
        description="Atualiza completamente uma proposição existente",
        tags=["proposições"],
        request=ProposicaoSerializer,
        responses={200: ProposicaoSerializer},
    ),
    partial_update=extend_schema(
        summary="Atualizar proposição parcialmente",
        description="Atualiza parcialmente uma proposição existente",
        tags=["proposições"],
        request=ProposicaoSerializer,
        responses={200: ProposicaoSerializer},
    ),
    destroy=extend_schema(
        summary="Excluir proposição",
        description="Remove uma proposição existente",
        tags=["proposições"],
        responses={204: None},
    ),
)
class ProposicaoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para o modelo Proposicao.
    
    Fornece as ações CRUD padrão:
    - list: GET /api/proposicoes/
    - create: POST /api/proposicoes/
    - retrieve: GET /api/proposicoes/{id}/
    - update: PUT /api/proposicoes/{id}/
    - partial_update: PATCH /api/proposicoes/{id}/
    - destroy: DELETE /api/proposicoes/{id}/
    """
    
    queryset = Proposicao.objects.all()
    serializer_class = ProposicaoSerializer
    permission_classes = [AllowAny]  # Allow all operations for now
    pagination_class = None  # Disable pagination for now


@extend_schema_view(
    list=extend_schema(
        summary="Listar eixos (Power BI)",
        description="Retorna uma lista de todos os eixos com contagem de temas para Power BI",
        tags=["power-bi"],
        responses={200: EixoReadOnlySerializer(many=True)},
    ),
    retrieve=extend_schema(
        summary="Obter eixo (Power BI)",
        description="Retorna detalhes de um eixo específico com contagem de temas",
        tags=["power-bi"],
        responses={200: EixoReadOnlySerializer},
    ),
)
class EixoReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet read-only para o modelo Eixo otimizado para Power BI.
    
    Fornece apenas operações de leitura:
    - list: GET /api/bi/eixos/
    - retrieve: GET /api/bi/eixos/{id}/
    """
    
    queryset = Eixo.objects.prefetch_related('temas').all()
    serializer_class = EixoReadOnlySerializer
    permission_classes = [AllowAny]
    pagination_class = None
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['nome']
    ordering_fields = ['id', 'nome', 'created_at']
    ordering = ['id']


@extend_schema_view(
    list=extend_schema(
        summary="Listar temas (Power BI)",
        description="Retorna uma lista de todos os temas com dados do eixo e contagem de proposições",
        tags=["power-bi"],
        responses={200: TemaReadOnlySerializer(many=True)},
    ),
    retrieve=extend_schema(
        summary="Obter tema (Power BI)",
        description="Retorna detalhes de um tema específico com dados do eixo e contagem de proposições",
        tags=["power-bi"],
        responses={200: TemaReadOnlySerializer},
    ),
)
class TemaReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet read-only para o modelo Tema otimizado para Power BI.
    
    Fornece apenas operações de leitura:
    - list: GET /api/bi/temas/
    - retrieve: GET /api/bi/temas/{id}/
    """
    
    queryset = Tema.objects.select_related('eixo').prefetch_related('proposicoes').all()
    serializer_class = TemaReadOnlySerializer
    permission_classes = [AllowAny]
    pagination_class = None
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['eixo__id', 'eixo__nome']
    search_fields = ['nome', 'eixo__nome']
    ordering_fields = ['id', 'nome', 'eixo__id', 'created_at']
    ordering = ['eixo__id', 'nome']


@extend_schema_view(
    list=extend_schema(
        summary="Listar proposições (Power BI)",
        description="Retorna uma lista de todas as proposições com dados completos do tema e eixo",
        tags=["power-bi"],
        responses={200: ProposicaoReadOnlySerializer(many=True)},
    ),
    retrieve=extend_schema(
        summary="Obter proposição (Power BI)",
        description="Retorna detalhes de uma proposição específica com dados completos do tema e eixo",
        tags=["power-bi"],
        responses={200: ProposicaoReadOnlySerializer},
    ),
)
class ProposicaoReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet read-only para o modelo Proposicao otimizado para Power BI.
    
    Fornece apenas operações de leitura:
    - list: GET /api/bi/proposicoes/
    - retrieve: GET /api/bi/proposicoes/{id}/
    """
    
    queryset = Proposicao.objects.select_related('tema__eixo').all()
    serializer_class = ProposicaoReadOnlySerializer
    permission_classes = [AllowAny]
    pagination_class = None
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['tipo', 'ano', 'tema__id', 'tema__nome', 'tema__eixo__id', 'tema__eixo__nome']
    search_fields = ['tipo', 'tema__nome', 'tema__eixo__nome']
    ordering_fields = ['id', 'tipo', 'numero', 'ano', 'tema__nome', 'created_at']
    ordering = ['tema__nome', 'ano', 'numero']


@extend_schema_view(
    list=extend_schema(
        summary="Listar atividades do Senado",
        description="Retorna uma lista de todas as atividades de proposições no Senado Federal",
        tags=["atividades"],
        parameters=[
            OpenApiParameter(
                name='proposicao',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Filtrar por ID da proposição'
            ),
            OpenApiParameter(
                name='data_inicio',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='Filtrar por data de início específica (YYYY-MM-DD)'
            ),
            OpenApiParameter(
                name='sigla_situacao',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filtrar por sigla da situação'
            ),
        ],
        responses={200: SenadoActivityHistorySerializer(many=True)},
    ),
    retrieve=extend_schema(
        summary="Obter atividade do Senado",
        description="Retorna detalhes de uma atividade específica do Senado Federal",
        tags=["atividades"],
        responses={200: SenadoActivityHistorySerializer},
    ),
)
class SenadoActivityHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet read-only para o modelo SenadoActivityHistory.
    
    Fornece apenas operações de leitura:
    - list: GET /api/atividades/senado/
    - retrieve: GET /api/atividades/senado/{id}/
    """
    
    queryset = SenadoActivityHistory.objects.select_related('proposicao').all()
    serializer_class = SenadoActivityHistorySerializer
    permission_classes = [AllowAny]
    pagination_class = None
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['proposicao', 'data_inicio', 'sigla_situacao']
    search_fields = ['descricao']
    ordering_fields = ['id', 'data_inicio', 'id_situacao', 'created_at']
    ordering = ['-data_inicio', '-id_situacao']


@extend_schema_view(
    list=extend_schema(
        summary="Listar atividades da Câmara",
        description="Retorna uma lista de todas as atividades de proposições na Câmara dos Deputados",
        tags=["atividades"],
        parameters=[
            OpenApiParameter(
                name='proposicao',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Filtrar por ID da proposição'
            ),
            OpenApiParameter(
                name='data_hora',
                type=OpenApiTypes.DATETIME,
                location=OpenApiParameter.QUERY,
                description='Filtrar por data e hora específica'
            ),
            OpenApiParameter(
                name='sigla_orgao',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filtrar por sigla do órgão'
            ),
            OpenApiParameter(
                name='cod_tipo_tramitacao',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filtrar por código do tipo de tramitação'
            ),
        ],
        responses={200: CamaraActivityHistorySerializer(many=True)},
    ),
    retrieve=extend_schema(
        summary="Obter atividade da Câmara",
        description="Retorna detalhes de uma atividade específica da Câmara dos Deputados",
        tags=["atividades"],
        responses={200: CamaraActivityHistorySerializer},
    ),
)
class CamaraActivityHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet read-only para o modelo CamaraActivityHistory.
    
    Fornece apenas operações de leitura:
    - list: GET /api/atividades/camara/
    - retrieve: GET /api/atividades/camara/{id}/
    """
    
    queryset = CamaraActivityHistory.objects.select_related('proposicao').all()
    serializer_class = CamaraActivityHistorySerializer
    permission_classes = [AllowAny]
    pagination_class = None
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['proposicao', 'sigla_orgao', 'cod_tipo_tramitacao', 'ambito', 'apreciacao']
    search_fields = ['despacho', 'descricao_tramitacao', 'descricao_situacao']
    ordering_fields = ['id', 'data_hora', 'sequencia', 'created_at']
    ordering = ['-data_hora', '-sequencia']
