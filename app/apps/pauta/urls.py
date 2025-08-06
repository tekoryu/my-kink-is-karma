from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TemaViewSet, ProposicaoViewSet

# Configuração do router para o ViewSet
router = DefaultRouter()
router.register(r'temas', TemaViewSet, basename='tema')
router.register(r'proposicoes', ProposicaoViewSet, basename='proposicao')

app_name = 'pauta'

urlpatterns = [
    path('api/', include(router.urls)),
] 