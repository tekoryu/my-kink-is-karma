import logging
import time
from typing import Dict, Optional
from django.utils import timezone

from .data_fetcher_service import DataFetcherService
from .data_processing_service import DataProcessingService
from .activity_sync_service import ActivitySyncService
from .selection_service import SelectionService

logger = logging.getLogger(__name__)


class SyncOrchestratorService:
    """
    Orchestrates the complete synchronization workflow.
    
    Responsibilities:
    - Coordinate data fetching and processing
    - Handle sync workflow logic
    - Manage batch operations
    - Delegate to specialized services
    """
    
    def __init__(self):
        self.fetcher = DataFetcherService()
        self.processor = DataProcessingService()
        self.activity_sync = ActivitySyncService()
        self.selection = SelectionService()
    
    def sync_proposicao(self, proposicao) -> bool:
        """
        Synchronize a single proposição with external APIs.
        
        Workflow:
        1. Fetch raw data from Senado and Câmara APIs
        2. Process raw data into structured format
        3. Apply processed data to proposição
        4. Update derived fields and selection
        
        Args:
            proposicao: Proposicao instance
            
        Returns:
            bool: True if synchronization was successful, False otherwise
        """
        try:
            logger.info(f"Starting sync for proposition: {proposicao.identificador_completo}")
            
            # Step 1: Fetch raw data from external APIs
            raw_senado_data = self.fetcher.fetch_proposicao_senado(
                proposicao.tipo, proposicao.numero, proposicao.ano
            )
            
            # Step 2: Process Senado data
            senado_data = None
            if raw_senado_data:
                senado_data = self.processor.process_senado_raw_data(
                    raw_senado_data, proposicao.tipo, proposicao.numero, proposicao.ano
                )
            
            # Step 3: Fetch and process Câmara data if needed
            camara_data = None
            if not senado_data or not senado_data.get('iniciadora'):
                # Fetch Câmara data
                search_data = self.fetcher.fetch_proposicao_camara_search(
                    proposicao.tipo, proposicao.numero, proposicao.ano
                )
                
                if search_data and 'dados' in search_data and len(search_data['dados']) > 0:
                    cd_id = search_data['dados'][0]['id']
                    
                    # Fetch details and authors
                    details_data = self.fetcher.fetch_proposicao_camara_details(cd_id)
                    authors_data = self.fetcher.fetch_proposicao_camara_authors(cd_id)
                    
                    # Process Câmara data
                    camara_data = self.processor.process_camara_raw_data(
                        search_data, details_data, authors_data
                    )
            
            # Step 4: Apply processed data to proposição
            success = self.processor.process_proposicao_sync_data(
                proposicao, senado_data, camara_data
            )
            
            if success:
                # Step 5: Update derived fields
                try:
                    self.processor.update_derived_fields(proposicao)
                except Exception as e:
                    logger.warning(f"Error updating derived fields after sync: {e}")
                
                # Step 6: Update tema selection
                try:
                    self.selection.atualizar_selecao_tema(proposicao.tema)
                    logger.debug(f"Selection updated for tema '{proposicao.tema.nome}' after sync")
                except Exception as e:
                    logger.warning(f"Error updating tema selection after sync: {e}")
                
                logger.info(f"Successfully synchronized: {proposicao.identificador_completo}")
                return True
            else:
                logger.warning(f"Failed to synchronize: {proposicao.identificador_completo}")
                return False
                
        except Exception as e:
            logger.error(f"Error synchronizing proposition {proposicao.identificador_completo}: {e}")
            proposicao.erro_sincronizacao = str(e)
            proposicao.ultima_sincronizacao = None
            proposicao.save()
            return False
    
    def sync_all_proposicoes(self, limit: Optional[int] = None, force: bool = False) -> Dict[str, int]:
        """
        Synchronize multiple proposições with external APIs.
        
        Args:
            limit: Maximum number of proposições to process (None for all)
            force: If True, sync all proposições, even already synchronized ones
            
        Returns:
            Dict with synchronization statistics
        """
        from apps.pauta.models import Proposicao
        
        # Determine which proposições to sync
        if force:
            proposicoes = Proposicao.objects.all().order_by('created_at')
        else:
            proposicoes = Proposicao.objects.filter(
                ultima_sincronizacao__isnull=True
            ).order_by('created_at')
        
        if limit:
            proposicoes = proposicoes[:limit]
        
        total = proposicoes.count()
        sucessos = 0
        erros = 0
        
        logger.info(f"Starting batch sync for {total} proposições")
        
        # Process each proposição
        for proposicao in proposicoes:
            if self.sync_proposicao(proposicao):
                sucessos += 1
            else:
                erros += 1
            
            # Rate limiting pause between proposições
            time.sleep(0.5)
        
        logger.info(f"Batch sync completed: {sucessos} successes, {erros} errors")
        
        # Update selection for all temas after batch sync
        if sucessos > 0:
            try:
                logger.info("Updating selection for all proposições after batch sync")
                selecao_result = self.selection.atualizar_selecao_proposicoes()
                logger.info(f"Selection updated: {selecao_result}")
            except Exception as e:
                logger.warning(f"Error updating selection after batch sync: {e}")
        
        return {
            'total': total,
            'sucessos': sucessos,
            'erros': erros
        }
    
    def sync_activities_for_proposicao(self, proposicao) -> Dict[str, bool]:
        """
        Synchronize activity history for a single proposição.
        
        Args:
            proposicao: Proposicao instance
            
        Returns:
            Dict with sync results for each house
        """
        results = {
            'senado': False,
            'camara': False
        }
        
        try:
            # Sync Senado activities if sf_id exists
            if proposicao.sf_id:
                results['senado'] = self.activity_sync.sincronizar_atividades_senado(proposicao)
            
            # Sync Câmara activities if cd_id exists
            if proposicao.cd_id:
                results['camara'] = self.activity_sync.sincronizar_atividades_camara(proposicao)
            
            # Note: Derived fields (like current_house) are now updated automatically
            # via Django signals when activity history changes
            
            return results
            
        except Exception as e:
            logger.error(f"Error synchronizing activities for {proposicao.identificador_completo}: {e}")
            return results
    
    def sync_activities_all_proposicoes(self, limit: Optional[int] = None) -> Dict[str, int]:
        """
        Synchronize activity history for multiple proposições.
        
        Args:
            limit: Maximum number of proposições to process (None for all)
            
        Returns:
            Dict with synchronization statistics
        """
        from apps.pauta.models import Proposicao
        
        # Only sync proposições that have API IDs
        proposicoes = Proposicao.objects.filter(
            sf_id__isnull=False
        ).order_by('created_at')
        
        if limit:
            proposicoes = proposicoes[:limit]
        
        total = proposicoes.count()
        sucessos_senado = 0
        sucessos_camara = 0
        erros = 0
        
        logger.info(f"Starting activity sync for {total} proposições")
        
        for proposicao in proposicoes:
            try:
                results = self.sync_activities_for_proposicao(proposicao)
                
                if results['senado']:
                    sucessos_senado += 1
                if results['camara']:
                    sucessos_camara += 1
                
                # If neither succeeded, count as error
                if not (results['senado'] or results['camara']):
                    erros += 1
                
                # Rate limiting pause
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error syncing activities for {proposicao.identificador_completo}: {e}")
                erros += 1
        
        logger.info(f"Activity sync completed: {sucessos_senado} Senado, {sucessos_camara} Câmara, {erros} errors")
        
        return {
            'total': total,
            'sucessos_senado': sucessos_senado,
            'sucessos_camara': sucessos_camara,
            'erros': erros
        }
    
    def get_sync_statistics(self) -> Dict[str, int]:
        """
        Get current synchronization statistics.
        
        Returns:
            Dict with sync statistics
        """
        from apps.pauta.models import Proposicao
        
        total = Proposicao.objects.count()
        sincronizadas = Proposicao.objects.filter(ultima_sincronizacao__isnull=False).count()
        com_erro = Proposicao.objects.filter(erro_sincronizacao__isnull=False).count()
        pendentes = total - sincronizadas
        
        com_sf_id = Proposicao.objects.filter(sf_id__isnull=False).count()
        com_cd_id = Proposicao.objects.filter(cd_id__isnull=False).count()
        
        return {
            'total': total,
            'sincronizadas': sincronizadas,
            'pendentes': pendentes,
            'com_erro': com_erro,
            'com_sf_id': com_sf_id,
            'com_cd_id': com_cd_id
        }
