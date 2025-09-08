import logging
from typing import Optional, Dict, List
from datetime import datetime
from django.db.models import Max, Min
from django.utils import timezone

logger = logging.getLogger(__name__)


class DataProcessingService:
    """
    Serviços de processamento e enriquecimento de dados das proposições.

    Objetivos:
    - Preencher campos derivados (ex: current_house) com base nas atividades.
    - Realizar backfill de datas e campos quando possível a partir do histórico.
    - Executar rotinas em lote de processamento.
    """

    def update_derived_fields(self, proposicao) -> bool:
        """
        Atualiza campos derivados de uma `Proposicao` (ex.: current_house) a partir do histórico.
        """
        try:
            from apps.pauta.models import SenadoActivityHistory, CamaraActivityHistory

            # Última atividade em cada casa
            ultima_sf = (
                SenadoActivityHistory.objects
                .filter(proposicao=proposicao)
                .aggregate(ultima=Max('data'))
                .get('ultima')
            )
            ultima_cd = (
                CamaraActivityHistory.objects
                .filter(proposicao=proposicao)
                .aggregate(ultima=Max('data_hora'))
                .get('ultima')
            )

            novo_current_house: Optional[str] = None
            if ultima_sf and ultima_cd:
                # Comparar datas para decidir a casa com atividade mais recente
                # Convert datetime to date for proper comparison
                ultima_cd_date = ultima_cd.date() if hasattr(ultima_cd, 'date') else ultima_cd
                if ultima_cd_date > ultima_sf:
                    novo_current_house = 'CD'
                else:
                    novo_current_house = 'SF'
            elif ultima_cd:
                novo_current_house = 'CD'
            elif ultima_sf:
                novo_current_house = 'SF'

            if novo_current_house and proposicao.current_house != novo_current_house:
                proposicao.current_house = novo_current_house
                proposicao.save(update_fields=['current_house'])
                logger.info(
                    f"Atualizado current_house de {proposicao.identificador_completo} para {novo_current_house}"
                )

            # Backfill de data_apresentacao se ausente: pegar a mais antiga conhecida
            if not proposicao.data_apresentacao:
                primeira_sf = (
                    SenadoActivityHistory.objects
                    .filter(proposicao=proposicao)
                    .aggregate(primeira=Min('data'))
                    .get('primeira')
                )
                primeira_cd_date = (
                    CamaraActivityHistory.objects
                    .filter(proposicao=proposicao)
                    .aggregate(primeira=Min('data_hora'))
                    .get('primeira')
                )
                # Converter datetime -> date quando necessário
                if primeira_cd_date:
                    primeira_cd = primeira_cd_date.date()
                else:
                    primeira_cd = None

                candidates = [d for d in [primeira_sf, primeira_cd] if d is not None]
                if candidates:
                    nova_data = min(candidates)
                    proposicao.data_apresentacao = nova_data
                    proposicao.save(update_fields=['data_apresentacao'])
                    logger.info(
                        f"Backfill data_apresentacao de {proposicao.identificador_completo} para {nova_data}"
                    )

            return True
        except Exception as e:
            logger.error(f"Erro ao atualizar campos derivados de {proposicao}: {e}")
            return False

    def processar_todas_proposicoes(self, limit: Optional[int] = None) -> Dict[str, int]:
        """
        Executa processamento de campos derivados para várias proposições.
        """
        from apps.pauta.models import Proposicao

        qs = Proposicao.objects.all().order_by('created_at')
        if limit:
            qs = qs[:limit]

        total = qs.count()
        sucesso = 0
        erros = 0

        for prop in qs:
            if self.update_derived_fields(prop):
                sucesso += 1
            else:
                erros += 1

        return {'total': total, 'sucesso': sucesso, 'erros': erros}
    
    def process_senado_raw_data(self, raw_data: List[Dict], tipo: str, numero: int, ano: int) -> Optional[Dict]:
        """
        Process raw Senado API response into structured data.
        
        Args:
            raw_data: Raw API response from Senado
            tipo: Proposition type
            numero: Proposition number
            ano: Proposition year
            
        Returns:
            Processed data dict with sf_id, data_apresentacao, ementa, iniciadora, autor
        """
        try:
            if not isinstance(raw_data, list):
                return None
            
            # Search for specific proposition based on type, number and year
            for processo in raw_data:
                identificacao = processo.get('identificacao', '')
                
                # Check if identification contains type, number and year
                if (tipo in identificacao and 
                    str(numero) in identificacao and 
                    str(ano) in identificacao):
                    
                    # Extract basic data
                    sf_id = processo.get('id')
                    data_apresentacao = self._process_senado_date(processo)
                    ementa = self._extract_senado_ementa(processo)
                    
                    # Check if it's the initiating house
                    objetivo = processo.get('objetivo', '')
                    iniciadora = None
                    autor = None
                    
                    if objetivo == 'Iniciadora':
                        iniciadora = 'SF'
                        autor = self._extract_senado_autor(processo)
                    
                    return {
                        'sf_id': sf_id,
                        'data_apresentacao': data_apresentacao,
                        'ementa': ementa,
                        'iniciadora': iniciadora,
                        'autor': autor
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Error processing Senado response: {e}")
            return None
    
    def process_camara_raw_data(self, search_data: Dict, details_data: Dict, authors_data: Dict) -> Optional[Dict]:
        """
        Process raw Câmara API responses into structured data.
        
        Args:
            search_data: Raw search API response
            details_data: Raw details API response  
            authors_data: Raw authors API response
            
        Returns:
            Processed data dict with cd_id, iniciadora, ementa, data_apresentacao, autor
        """
        try:
            if not (search_data and details_data):
                return None
            
            # Extract CD ID from search results
            if 'dados' not in search_data or len(search_data['dados']) == 0:
                return None
            
            cd_id = search_data['dados'][0]['id']
            
            # Extract data from details
            if 'dados' not in details_data:
                return None
            
            proposicao = details_data['dados']
            
            ementa = proposicao.get('ementa')
            data_apresentacao = self._process_camara_date(proposicao.get('dataApresentacao'))
            
            # Process authors
            autor = self._process_camara_authors(authors_data)
            
            return {
                'cd_id': cd_id,
                'iniciadora': 'CD',  # Assume CD for propositions without SF initiadora
                'ementa': ementa,
                'data_apresentacao': data_apresentacao,
                'autor': autor
            }
            
        except Exception as e:
            logger.error(f"Error processing Câmara response: {e}")
            return None
    
    def process_proposicao_sync_data(self, proposicao, senado_data: Optional[Dict], camara_data: Optional[Dict]) -> bool:
        """
        Process and apply sync data to a proposição.
        
        Args:
            proposicao: Proposicao instance
            senado_data: Processed Senado data
            camara_data: Processed Câmara data
            
        Returns:
            True if data was found and applied, False otherwise
        """
        try:
            encontrou_dados = False
            
            # Always save sf_id if found
            if senado_data and senado_data.get('sf_id'):
                proposicao.sf_id = senado_data['sf_id']
                logger.info(f"SF ID found: {senado_data['sf_id']}")
                encontrou_dados = True
            
            # If Senado indicated it's the initiating house, use its data
            if senado_data and senado_data.get('iniciadora') == 'SF':
                proposicao.iniciadora = 'SF'
                if senado_data.get('autor'):
                    proposicao.autor = senado_data['autor']
                if senado_data.get('data_apresentacao'):
                    proposicao.data_apresentacao = senado_data['data_apresentacao']
                if senado_data.get('ementa'):
                    proposicao.ementa = senado_data['ementa']
                logger.info("Data extracted from Senado (initiating house)")
                encontrou_dados = True
            
            # If no initiating house defined, use Câmara data
            if not proposicao.iniciadora and camara_data:
                # Save cd_id
                if camara_data.get('cd_id'):
                    proposicao.cd_id = camara_data['cd_id']
                    logger.info(f"CD ID found: {camara_data['cd_id']}")
                    encontrou_dados = True
                
                # Assume initiating house = CD
                proposicao.iniciadora = 'CD'
                
                # Extract Câmara data
                if camara_data.get('autor'):
                    proposicao.autor = camara_data['autor']
                if camara_data.get('data_apresentacao'):
                    proposicao.data_apresentacao = camara_data['data_apresentacao']
                if camara_data.get('ementa'):
                    proposicao.ementa = camara_data['ementa']
                
                logger.info("Data extracted from Câmara (initiating house determined as CD)")
                encontrou_dados = True
            
            # Check if proposition was found in any API
            if not encontrou_dados:
                # Proposition not found in any API
                proposicao.ultima_sincronizacao = None
                proposicao.erro_sincronizacao = 'NOT FOUND'
                proposicao.save()
                logger.warning(f"Proposition {proposicao.identificador_completo} not found in any API")
                return False
            else:
                # Mark as successfully synchronized
                proposicao.ultima_sincronizacao = timezone.now()
                proposicao.erro_sincronizacao = None
                proposicao.save()
                logger.info(f"Proposition {proposicao.identificador_completo} synchronized successfully")
                return True
                
        except Exception as e:
            logger.error(f"Error processing sync data for {proposicao.identificador_completo}: {e}")
            proposicao.erro_sincronizacao = str(e)
            proposicao.ultima_sincronizacao = None
            proposicao.save()
            return False
    
    def _process_senado_date(self, processo: Dict) -> Optional[str]:
        """Extract presentation date from Senado process."""
        try:
            data_str = processo.get('dataApresentacao')
            return self._process_date(data_str)
        except Exception:
            return None
    
    def _process_camara_date(self, data_str: str) -> Optional[str]:
        """Process presentation date from Câmara (format 2023-09-11T12:24)."""
        if not data_str:
            return None
        try:
            # Remove time part if present
            if 'T' in data_str:
                data_str = data_str.split('T')[0]
            # Check if already in correct format
            datetime.strptime(data_str, '%Y-%m-%d')
            return data_str
        except (ValueError, AttributeError):
            return None
    
    def _extract_senado_ementa(self, processo: Dict) -> Optional[str]:
        """Extract ementa from Senado process."""
        try:
            return processo.get('ementa')
        except Exception:
            return None
    
    def _extract_senado_autor(self, processo: Dict) -> Optional[str]:
        """Extract author from Senado process autoria structure."""
        try:
            autoria = processo.get('autoria')
            return autoria if isinstance(autoria, str) else None
        except Exception:
            return None
    
    def _process_camara_authors(self, authors_data: Dict) -> Optional[str]:
        """Process Câmara authors data and format appropriately."""
        try:
            if not authors_data or 'dados' not in authors_data or len(authors_data['dados']) == 0:
                return None
            
            nome = authors_data['dados'][0].get('nome', '')
            return nome if nome else None
            
        except Exception as e:
            logger.error(f"Error processing Câmara authors: {e}")
            return None
    
    def _process_date(self, data_str: str) -> Optional[str]:
        """
        Process date string to format compatible with DateField.
        
        Args:
            data_str: Date string from API
            
        Returns:
            String in YYYY-MM-DD format or None if invalid
        """
        if not data_str:
            return None
            
        try:
            # Common format: "2023-01-15T00:00:00"
            if 'T' in data_str:
                data_str = data_str.split('T')[0]
            
            # Check if already in correct format
            if len(data_str) == 10 and data_str.count('-') == 2:
                # Validate if it's a valid date
                datetime.strptime(data_str, '%Y-%m-%d')
                return data_str
            
            # Other formats can be added here
            logger.warning(f"Unrecognized date format: {data_str}")
            return None
            
        except (ValueError, AttributeError) as e:
            logger.warning(f"Error processing date '{data_str}': {e}")
            return None


