from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.pagination import PageNumberPagination
from .models import Tema
from .serializers import TemaSerializer


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
