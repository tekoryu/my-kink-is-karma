from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.pagination import PageNumberPagination
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from .models import Tema
from .serializers import TemaSerializer


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
