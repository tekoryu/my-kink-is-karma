import requests
import logging
from typing import Dict, Optional, List
from .api_config import APIConfig, RateLimiter

logger = logging.getLogger(__name__)


class DataFetcherService:
    """
    Pure data fetching service for external APIs.
    
    Responsibilities:
    - Make HTTP requests to Senado and Câmara APIs
    - Handle rate limiting and error handling
    - Return raw API responses without processing
    - No business logic or data transformation
    """
    
    def __init__(self):
        self.rate_limiter = RateLimiter()
    
    def fetch_proposicao_senado(self, tipo: str, numero: int, ano: int) -> Optional[List[Dict]]:
        """
        Fetch raw proposição data from Senado API.
        
        Args:
            tipo: Tipo da proposição (PL, PEC, etc.)
            numero: Número da proposição
            ano: Ano da proposição
            
        Returns:
            Raw API response data or None if error/not found
        """
        self.rate_limiter.rate_limit_senado()
        
        search_url = f"{APIConfig.SENADO_BASE_URL}/processo"
        
        params = {
            'sigla': tipo,
            'numero': numero,
            'ano': ano
        }
        
        try:
            response = requests.get(
                search_url, 
                params=params,
                headers=APIConfig.DEFAULT_HEADERS, 
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Successfully fetched Senado data for {tipo} {numero}/{ano}")
                return data if isinstance(data, list) else None
            else:
                logger.warning(f"Senado API returned status {response.status_code} for {tipo} {numero}/{ano}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error fetching Senado data for {tipo} {numero}/{ano}: {e}")
            return None
    
    def fetch_proposicao_camara_search(self, tipo: str, numero: int, ano: int) -> Optional[Dict]:
        """
        Fetch proposição search results from Câmara API.
        
        Args:
            tipo: Tipo da proposição (PL, PEC, etc.)
            numero: Número da proposição
            ano: Ano da proposição
            
        Returns:
            Raw search API response or None if error/not found
        """
        self.rate_limiter.rate_limit_camara()
        
        search_url = f"{APIConfig.CAMARA_BASE_URL}/proposicoes"
        
        params = {
            'siglaTipo': tipo,
            'numero': numero,
            'ano': ano
        }
        
        try:
            response = requests.get(
                search_url, 
                params=params, 
                headers=APIConfig.DEFAULT_HEADERS, 
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Successfully fetched Câmara search data for {tipo} {numero}/{ano}")
                return data
            else:
                logger.warning(f"Câmara search API returned status {response.status_code} for {tipo} {numero}/{ano}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error fetching Câmara search data for {tipo} {numero}/{ano}: {e}")
            return None
    
    def fetch_proposicao_camara_details(self, cd_id: int) -> Optional[Dict]:
        """
        Fetch detailed proposição data from Câmara API using ID.
        
        Args:
            cd_id: Câmara proposição ID
            
        Returns:
            Raw details API response or None if error/not found
        """
        self.rate_limiter.rate_limit_camara()
        
        details_url = f"{APIConfig.CAMARA_BASE_URL}/proposicoes/{cd_id}"
        
        try:
            response = requests.get(details_url, headers=APIConfig.DEFAULT_HEADERS, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Successfully fetched Câmara details for ID {cd_id}")
                return data
            else:
                logger.warning(f"Câmara details API returned status {response.status_code} for ID {cd_id}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error fetching Câmara details for ID {cd_id}: {e}")
            return None
    
    def fetch_proposicao_camara_authors(self, cd_id: int) -> Optional[Dict]:
        """
        Fetch proposição authors from Câmara API.
        
        Args:
            cd_id: Câmara proposição ID
            
        Returns:
            Raw authors API response or None if error/not found
        """
        self.rate_limiter.rate_limit_camara()
        
        authors_url = f"{APIConfig.CAMARA_BASE_URL}/proposicoes/{cd_id}/autores"
        
        try:
            response = requests.get(authors_url, headers=APIConfig.DEFAULT_HEADERS, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Successfully fetched Câmara authors for ID {cd_id}")
                return data
            else:
                logger.warning(f"Câmara authors API returned status {response.status_code} for ID {cd_id}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error fetching Câmara authors for ID {cd_id}: {e}")
            return None
    
    def fetch_deputado_details(self, uri: str) -> Optional[Dict]:
        """
        Fetch detailed deputado data from Câmara API.
        
        Args:
            uri: Deputado URI from API
            
        Returns:
            Raw deputado API response or None if error/not found
        """
        self.rate_limiter.rate_limit_camara()
        
        try:
            response = requests.get(uri, headers=APIConfig.DEFAULT_HEADERS, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Successfully fetched deputado details from {uri}")
                return data
            else:
                logger.warning(f"Deputado details API returned status {response.status_code} for {uri}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error fetching deputado details from {uri}: {e}")
            return None
    
    def fetch_atividades_senado(self, sf_id: int) -> Optional[Dict]:
        """
        Fetch activity history from Senado API.
        
        Args:
            sf_id: Senado proposição ID
            
        Returns:
            Raw activity API response or None if error/not found
        """
        self.rate_limiter.rate_limit_senado()
        
        activities_url = f"{APIConfig.SENADO_BASE_URL}/processo/{sf_id}/informesLegislativos"
        
        try:
            response = requests.get(activities_url, headers=APIConfig.DEFAULT_HEADERS, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Successfully fetched Senado activities for ID {sf_id}")
                return data
            else:
                logger.warning(f"Senado activities API returned status {response.status_code} for ID {sf_id}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error fetching Senado activities for ID {sf_id}: {e}")
            return None
    
    def fetch_atividades_camara(self, cd_id: int) -> Optional[Dict]:
        """
        Fetch activity history from Câmara API.
        
        Args:
            cd_id: Câmara proposição ID
            
        Returns:
            Raw activity API response or None if error/not found
        """
        self.rate_limiter.rate_limit_camara()
        
        activities_url = f"{APIConfig.CAMARA_BASE_URL}/proposicoes/{cd_id}/tramitacoes"
        
        try:
            response = requests.get(activities_url, headers=APIConfig.DEFAULT_HEADERS, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Successfully fetched Câmara activities for ID {cd_id}")
                return data
            else:
                logger.warning(f"Câmara activities API returned status {response.status_code} for ID {cd_id}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error fetching Câmara activities for ID {cd_id}: {e}")
            return None
