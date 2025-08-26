from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    EixoViewSet, TemaViewSet, ProposicaoViewSet,
    EixoReadOnlyViewSet, TemaReadOnlyViewSet, ProposicaoReadOnlyViewSet,
    SenadoActivityHistoryViewSet, CamaraActivityHistoryViewSet
)

# Configuração do roteador para o ViewSet
router = DefaultRouter()
router.register(r'eixos', EixoViewSet, basename='eixo')
router.register(r'temas', TemaViewSet, basename='tema')
router.register(r'proposicoes', ProposicaoViewSet, basename='proposicao')

# Router para endpoints Power BI (read-only)
bi_router = DefaultRouter()
bi_router.register(r'eixos', EixoReadOnlyViewSet, basename='bi-eixo')
bi_router.register(r'temas', TemaReadOnlyViewSet, basename='bi-tema')
bi_router.register(r'proposicoes', ProposicaoReadOnlyViewSet, basename='bi-proposicao')

# Router para endpoints de atividades (read-only)
activity_router = DefaultRouter()
activity_router.register(r'senado', SenadoActivityHistoryViewSet, basename='senado-activity')
activity_router.register(r'camara', CamaraActivityHistoryViewSet, basename='camara-activity')

app_name = 'pauta'

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/bi/', include(bi_router.urls)),
    path('api/atividades/', include(activity_router.urls)),
]