import time
import logging

logger = logging.getLogger(__name__)


class APIConfig:
    """
    Configuração centralizada para APIs do Senado e Câmara.
    """
    
    # URLs das APIs
    SENADO_BASE_URL = "https://legis.senado.leg.br/dadosabertos"
    CAMARA_BASE_URL = "https://dadosabertos.camara.leg.br/api/v2"
    
    # Headers padrão
    DEFAULT_HEADERS = {
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    # Rate limiting
    SENADO_RATE_LIMIT = 10  # requisições por segundo
    CAMARA_RATE_LIMIT = 15  # requisições por segundo


class RateLimiter:
    """
    Controle de rate limiting compartilhado para as APIs.
    """
    
    def __init__(self):
        self.last_senado_request = 0
        self.last_camara_request = 0
    
    def rate_limit_senado(self):
        """Aplica rate limiting para a API do Senado"""
        current_time = time.time()
        time_since_last = current_time - self.last_senado_request
        if time_since_last < (1.0 / APIConfig.SENADO_RATE_LIMIT):
            sleep_time = (1.0 / APIConfig.SENADO_RATE_LIMIT) - time_since_last
            time.sleep(sleep_time)
        self.last_senado_request = time.time()
    
    def rate_limit_camara(self):
        """Aplica rate limiting para a API da Câmara"""
        current_time = time.time()
        time_since_last = current_time - self.last_camara_request
        if time_since_last < (1.0 / APIConfig.CAMARA_RATE_LIMIT):
            sleep_time = (1.0 / APIConfig.CAMARA_RATE_LIMIT) - time_since_last
            time.sleep(sleep_time)
        self.last_camara_request = time.time()
