from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TemaViewSet, ProposicaoViewSet,
    EixoReadOnlyViewSet, TemaReadOnlyViewSet, ProposicaoReadOnlyViewSet
)

# Configuração do router para o ViewSet
router = DefaultRouter()
router.register(r'temas', TemaViewSet, basename='tema')
router.register(r'proposicoes', ProposicaoViewSet, basename='proposicao')

# Router para endpoints Power BI (read-only)
bi_router = DefaultRouter()
bi_router.register(r'eixos', EixoReadOnlyViewSet, basename='bi-eixo')
bi_router.register(r'temas', TemaReadOnlyViewSet, basename='bi-tema')
bi_router.register(r'proposicoes', ProposicaoReadOnlyViewSet, basename='bi-proposicao')

app_name = 'pauta'

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/bi/', include(bi_router.urls)),
] 