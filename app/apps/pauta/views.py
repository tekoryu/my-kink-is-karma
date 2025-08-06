from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import ValidationError
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from .models import Tema, Proposicao
from .serializers import TemaSerializer, ProposicaoSerializer
from .services import consultar_e_salvar_dados_iniciais


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


@extend_schema_view(
    list=extend_schema(
        summary="Listar proposições",
        description="Retorna uma lista de todas as proposições cadastradas",
        tags=["proposições"],
        responses={200: ProposicaoSerializer(many=True)},
    ),
    create=extend_schema(
        summary="Criar proposição",
        description="Cria uma nova proposição e valida na API externa",
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
    
    Na criação, valida a proposição na API externa de forma não-bloqueante.
    """
    
    queryset = Proposicao.objects.all()
    serializer_class = ProposicaoSerializer
    permission_classes = [AllowAny]  # Allow all operations for now
    pagination_class = None  # Disable pagination for now
    
    def perform_create(self, serializer):
        """
        Salva a proposição e valida na API externa.
        
        Se a validação falhar, remove a proposição e levanta ValidationError.
        """
        proposicao = serializer.save()
        
        # Consulta dados na API externa de forma não-bloqueante
        dados = consultar_e_salvar_dados_iniciais(proposicao)
        if dados is None:
            # Remove a proposição se a consulta falhar
            proposicao.delete()
            raise ValidationError(
                "A proposição não foi encontrada na API pública ou é inválida."
            )
