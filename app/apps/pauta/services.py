import logging
from typing import Dict, Optional

from .services_impl.sync_orchestrator_service import SyncOrchestratorService
from .services_impl.data_fetcher_service import DataFetcherService
from .services_impl.data_processing_service import DataProcessingService
from .services_impl.activity_sync_service import ActivitySyncService
from .services_impl.selection_service import SelectionService

logger = logging.getLogger(__name__)


class APISyncService:
    """
    Main service for synchronizing data from Senado Federal and Câmara dos Deputados APIs.
    
    This is now a facade/adapter that delegates to specialized services:
    - SyncOrchestratorService: Coordinates the sync workflow
    - DataFetcherService: Handles external API calls
    - DataProcessingService: Processes raw API data
    - ActivitySyncService: Manages activity history
    - SelectionService: Handles proposition selection logic
    
    Maintains backward compatibility with existing code.
    """
    
    def __init__(self):
        # Initialize specialized services
        self.orchestrator = SyncOrchestratorService()
        self.fetcher = DataFetcherService()
        self.data_processing = DataProcessingService()
        self.activity_sync = ActivitySyncService()
        self.selection = SelectionService()
    
    # =============================================================================
    # MAIN SYNC METHODS - Delegate to SyncOrchestratorService
    # =============================================================================
    
    def sincronizar_proposicao(self, proposicao) -> bool:
        """
        Synchronize a single proposição with external APIs.
        
        Delegates to SyncOrchestratorService for the complete workflow.
        """
        return self.orchestrator.sync_proposicao(proposicao)
    
    def sincronizar_todas_proposicoes(self, limit: Optional[int] = None, force: bool = False) -> Dict[str, int]:
        """
        Synchronize multiple proposições with external APIs.
        
        Delegates to SyncOrchestratorService for batch processing.
        """
        return self.orchestrator.sync_all_proposicoes(limit=limit, force=force)
    
    # =============================================================================
    # ACTIVITY SYNC METHODS - Delegate to ActivitySyncService
    # =============================================================================
    
    def sincronizar_atividades_senado(self, proposicao) -> bool:
        """Delegates to ActivitySyncService."""
        return self.activity_sync.sincronizar_atividades_senado(proposicao)
    
    def sincronizar_atividades_camara(self, proposicao) -> bool:
        """Delegates to ActivitySyncService."""
        return self.activity_sync.sincronizar_atividades_camara(proposicao)
    
    def sincronizar_atividades_todas_proposicoes(self, limit: Optional[int] = None) -> Dict[str, int]:
        """
        Synchronize activity history for multiple proposições.
        
        Delegates to SyncOrchestratorService.
        """
        return self.orchestrator.sync_activities_all_proposicoes(limit=limit)
    
    # Backward compatibility shims for activity creation
    def _criar_atividade_senado(self, proposicao, informe: Dict) -> bool:
        """Backward-compat shim: delegate to ActivitySyncService."""
        return self.activity_sync._criar_atividade_senado(proposicao, informe)
    
    def _criar_atividade_camara(self, proposicao, tramitacao: Dict) -> bool:
        """Backward-compat shim: delegate to ActivitySyncService."""
        return self.activity_sync._criar_atividade_camara(proposicao, tramitacao)
    
    # =============================================================================
    # SELECTION METHODS - Delegate to SelectionService
    # =============================================================================
    
    def atualizar_selecao_tema(self, tema) -> bool:
        """Delegates to SelectionService."""
        return self.selection.atualizar_selecao_tema(tema)

    def atualizar_selecao_proposicoes(self) -> Dict[str, int]:
        """Delegates to SelectionService."""
        return self.selection.atualizar_selecao_proposicoes()
    
    # =============================================================================
    # DIRECT DATA ACCESS METHODS (for testing/debugging)
    # =============================================================================
    
    def buscar_proposicao_senado(self, tipo: str, numero: int, ano: int) -> Optional[Dict]:
        """
        Fetch raw Senado data and process it.
        
        Delegates to DataFetcherService and DataProcessingService.
        """
        raw_data = self.fetcher.fetch_proposicao_senado(tipo, numero, ano)
        if raw_data:
            return self.data_processing.process_senado_raw_data(raw_data, tipo, numero, ano)
        return None
    
    def buscar_proposicao_camara(self, tipo: str, numero: int, ano: int) -> Optional[Dict]:
        """
        Fetch raw Câmara data and process it.
        
        Delegates to DataFetcherService and DataProcessingService.
        """
        search_data = self.fetcher.fetch_proposicao_camara_search(tipo, numero, ano)
        if search_data and 'dados' in search_data and len(search_data['dados']) > 0:
            cd_id = search_data['dados'][0]['id']
            details_data = self.fetcher.fetch_proposicao_camara_details(cd_id)
            authors_data = self.fetcher.fetch_proposicao_camara_authors(cd_id)
            
            return self.data_processing.process_camara_raw_data(
                search_data, details_data, authors_data
            )
        return None
    
    # =============================================================================
    # UTILITY METHODS
    # =============================================================================
    
    def get_sync_statistics(self) -> Dict[str, int]:
        """Get current synchronization statistics."""
        return self.orchestrator.get_sync_statistics()