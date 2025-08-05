from django.apps import AppConfig


class PautaConfig(AppConfig):
    """
    Configuração do aplicativo Pauta.
    
    Este aplicativo gerencia temas e proposições legislativas para monitoramento
    automático através de APIs públicas.
    """
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.pauta'
    verbose_name = 'Pauta Legislativa'
