# API Synchronization Service

This document describes the API synchronization service created for the legislative data system, which automatically fetches and updates Proposicao records with data from the Senado Federal and Câmara dos Deputados APIs.

## Overview

The service provides automated synchronization of legislative proposal data from two Brazilian legislative APIs:
- **Senado Federal API**: `https://legis.senado.leg.br/dadosabertos/`
- **Câmara dos Deputados API**: `https://dadosabertos.camara.leg.br/api/v2/`

## Features

- ✅ **Dual API Support**: Fetches data from both Senado and Câmara APIs
- ✅ **Rate Limiting**: Respects API rate limits (Senado: 10 req/s, Câmara: 15 req/s)
- ✅ **Error Handling**: Comprehensive error handling and logging
- ✅ **Flexible Matching**: Handles proposições found in one, both, or neither API
- ✅ **Data Extraction**: Captures author, presentation date, and house of origin
- ✅ **Incremental Sync**: Only processes unsynchronized proposições
- ✅ **Admin Integration**: Full Django admin interface support
- ✅ **Activity History**: Tracks legislative activities from both houses

## Data Fields Captured

The service populates the following fields in the `Proposicao` model:

| Field | Description | Source |
|-------|-------------|---------|
| `sf_id` | Senado Federal API ID | Senado API |
| `cd_id` | Câmara dos Deputados API ID | Câmara API |
| `autor` | Author name | Both APIs |
| `data_apresentacao` | Presentation date | Both APIs |
| `casa_inicial` | House where proposal originated | Both APIs |
| `ultima_sincronizacao` | Last sync timestamp | System |
| `erro_sincronizacao` | Error message if sync failed | System |

## Management Commands

### Primary Command: `sync_proposicoes`

The main command for synchronizing proposições with the APIs.

```bash
# Basic usage - sync all unsynchronized proposições
docker compose run --rm app sh -c "python manage.py sync_proposicoes"

# Sync with limit
docker compose run --rm app sh -c "python manage.py sync_proposicoes --limit 10"

# Sync specific proposição by ID
docker compose run --rm app sh -c "python manage.py sync_proposicoes --proposicao-id 123"

# Force re-sync all proposições (including already synced)
docker compose run --rm app sh -c "python manage.py sync_proposicoes --force"

# Dry run - test without saving changes
docker compose run --rm app sh -c "python manage.py sync_proposicoes --dry-run --limit 5"
```

### Command Options

| Option | Type | Description |
|--------|------|-------------|
| `--limit` | int | Maximum number of proposições to process |
| `--proposicao-id` | int | Sync specific proposição by database ID |
| `--force` | flag | Re-sync all proposições, including already synced ones |
| `--dry-run` | flag | Test mode - shows what would be synced without saving |

### Examples

#### Sync All Proposições
```bash
docker compose run --rm app sh -c "python manage.py sync_proposicoes"
```
**Output:**
```
Sincronizando apenas proposições não sincronizadas
Total de proposições a processar: 43
Sincronização concluída: 43 sucessos, 0 erros
```

#### Test Sync with Limit
```bash
docker compose run --rm app sh -c "python manage.py sync_proposicoes --dry-run --limit 3"
```
**Output:**
```
Sincronizando apenas proposições não sincronizadas
Total de proposições a processar: 43
Modo dry-run: não serão feitas alterações no banco
Mostrando amostra de 3 proposições:
- MSC 209/2023
- PL 4381/2023
- PLP 108/2024
```

#### Sync Specific Proposição
```bash
docker compose run --rm app sh -c "python manage.py sync_proposicoes --proposicao-id 32"
```
**Output:**
```
Sincronizando proposição específica: MSC 209/2023
Proposição MSC 209/2023 sincronizada com sucesso
```

## API Integration Details

### Senado Federal API
- **Base URL**: `https://legis.senado.leg.br/dadosabertos/`
- **Endpoint**: `/processo`
- **Rate Limit**: 10 requests per second
- **Data Structure**: List of processes with identification, author, and presentation date

### Câmara dos Deputados API
- **Base URL**: `https://dadosabertos.camara.leg.br/api/v2/`
- **Endpoint**: `/proposicoes`
- **Authors Endpoint**: `/proposicoes/{id}/autores`
- **Rate Limit**: 15 requests per second
- **Data Structure**: JSON with `dados` array containing proposal information

### Matching Logic

The service matches proposições using:
1. **Tipo** (PL, PEC, MPV, etc.)
2. **Número** (proposal number)
3. **Ano** (year)

For Senado API: Searches through all processes and matches by identification string
For Câmara API: Uses direct search with `siglaTipo`, `numero`, and `ano` parameters

## Real-world Scenarios

The service handles all possible scenarios:

### 1. Found in Both APIs
```
PLP 108/2024:
- SF ID: 8746627
- CD ID: 2438459
- Autor: Câmara dos Deputados
- Casa: SF
- Data: 2024-11-11
```

### 2. Found in Câmara Only
```
PL 4920/2024:
- SF ID: None
- CD ID: 2480445
- Autor: Poder Executivo
- Casa: CD
- Data: None
```

### 3. Found in Senado Only
```
PL 365/2025:
- SF ID: 8832086
- CD ID: 2483498
- Autor: Senador Dr. Hiran (PP/RR)
- Casa: SF
- Data: 2025-05-19
```

### 4. Not Found in Either API
```
MSC 209/2023:
- SF ID: None
- CD ID: None
- Autor: None
- Casa: None
- Data: None
- Status: Still marked as synchronized (no error)
```

## Admin Interface

The Django admin interface provides:

### Proposicao List View
- **Columns**: Identifier, Theme, Author, Initial House, Has API Data, Last Sync
- **Filters**: Theme, Type, Year, Initial House, Sync Status
- **Search**: By type, number, theme name, author

### Proposicao Detail View
- **Identification**: Type, Number, Year
- **Organization**: Theme
- **API Data**: SF ID, CD ID, Author, Presentation Date, Initial House
- **Sync Info**: Last Sync, Error Messages (collapsed)

## Error Handling

The service includes comprehensive error handling:

- **API Timeouts**: 30-second timeout for all requests
- **Rate Limiting**: Automatic delays between requests
- **Network Errors**: Logged and tracked in `erro_sincronizacao` field
- **Data Parsing Errors**: Graceful handling of malformed responses
- **Missing Data**: Proposições not found are still marked as synchronized

## Logging

The service logs all activities:
- Sync start/completion
- Individual proposição processing
- API request results
- Errors and warnings

Logs can be viewed in Django's logging system or container logs.

## Performance Considerations

- **Rate Limiting**: Built-in delays prevent API overload
- **Incremental Processing**: Only unsynchronized proposições are processed
- **Batch Processing**: Can limit number of proposições per run
- **Error Recovery**: Failed syncs don't prevent others from processing

## Troubleshooting

### Common Issues

1. **No data captured**: Proposição may not exist in either API
2. **Partial data**: Proposição found in only one API
3. **Sync errors**: Check `erro_sincronizacao` field in admin
4. **Rate limiting**: Service automatically handles this

### Debug Commands

```bash
# Check sync status
docker compose run --rm app sh -c "python manage.py shell -c \"from apps.pauta.models import Proposicao; print(f'Synced: {Proposicao.objects.filter(ultima_sincronizacao__isnull=False).count()}'); print(f'With API data: {Proposicao.objects.filter(sf_id__isnull=False).count() + Proposicao.objects.filter(cd_id__isnull=False).count()}')\""

# Test specific proposição
docker compose run --rm app sh -c "python manage.py sync_proposicoes --proposicao-id 1 --dry-run"
```

## Future Enhancements

Potential improvements for the service:
- **Scheduled Sync**: Cron job integration
- **Webhook Support**: Real-time updates
- **Data Validation**: Enhanced error checking
- **Performance Metrics**: Sync statistics and monitoring
- **API Caching**: Reduce redundant requests

---

# Activity History Synchronization

The Activity History feature tracks legislative activities and procedural steps for each proposição in both houses of the Brazilian Congress.

## Overview

The Activity History system captures detailed procedural information from both legislative houses:
- **Senado Federal**: Legislative reports (`informesLegislativos`) from `/processo/{id}` endpoint
- **Câmara dos Deputados**: Procedural steps (`tramitacoes`) from `/proposicoes/{id}/tramitacoes` endpoint

## Features

- ✅ **Dual House Tracking**: Separate models for Senado and Câmara activities
- ✅ **Comprehensive Data Capture**: All available fields from both APIs
- ✅ **Read-only API Endpoints**: RESTful access to activity data
- ✅ **Admin Interface**: Full Django admin integration
- ✅ **Incremental Sync**: Only syncs proposições with API IDs
- ✅ **Rate Limiting**: Respects API limits during synchronization

## Data Models

### SenadoActivityHistory
Captures legislative reports from Senado Federal:

| Field | Description | Source |
|-------|-------------|---------|
| `id_informe` | Unique report ID | Senado API |
| `data` | Report date | Senado API |
| `descricao` | Detailed description | Senado API |
| `colegiado_*` | Committee information | Senado API |
| `ente_administrativo_*` | Administrative entity | Senado API |
| `sigla_situacao_iniciada` | Status code | Senado API |

### CamaraActivityHistory
Captures procedural steps from Câmara dos Deputados:

| Field | Description | Source |
|-------|-------------|---------|
| `sequencia` | Sequential number | Câmara API |
| `data_hora` | Date and time | Câmara API |
| `sigla_orgao` | Organ acronym | Câmara API |
| `descricao_tramitacao` | Procedure description | Câmara API |
| `despacho` | Dispatch text | Câmara API |
| `cod_tipo_tramitacao` | Procedure type code | Câmara API |

## Management Commands

### Primary Command: `sync_activity_history`

Synchronizes activity history for proposições with API IDs.

```bash
# Basic usage - sync all proposições with API IDs
docker compose run --rm app python manage.py sync_activity_history

# Sync with limit
docker compose run --rm app python manage.py sync_activity_history --limit 10

# Sync specific proposição
docker compose run --rm app python manage.py sync_activity_history --proposicao-id 123

# Sync only Senado activities
docker compose run --rm app python manage.py sync_activity_history --senado-only

# Sync only Câmara activities
docker compose run --rm app python manage.py sync_activity_history --camara-only

# Force re-sync (update existing records)
docker compose run --rm app python manage.py sync_activity_history --force
```

### Command Options

| Option | Type | Description |
|--------|------|-------------|
| `--limit` | int | Maximum number of proposições to process |
| `--proposicao-id` | int | Sync specific proposição by database ID |
| `--senado-only` | flag | Sync only Senado activities |
| `--camara-only` | flag | Sync only Câmara activities |
| `--force` | flag | Update existing activity records |

### Examples

#### Sync All Activity History
```bash
docker compose run --rm app python manage.py sync_activity_history
```
**Output:**
```
Iniciando sincronização de histórico de atividades...
Processando 25 proposições
[1/25] Processando PL 4381/2023...
  ✓ Senado: OK
  ✓ Câmara: OK
[2/25] Processando PLP 108/2024...
  ✓ Senado: OK
  ✓ Câmara: OK
...
==================================================
SINCRONIZAÇÃO CONCLUÍDA
==================================================
Total de proposições: 25
Senado (sucessos): 23
Câmara (sucessos): 25
Erros: 2
Tempo total: 45.32 segundos
```

#### Sync Specific Proposição
```bash
docker compose run --rm app python manage.py sync_activity_history --proposicao-id 1
```
**Output:**
```
Processando proposição específica: PL 4381/2023
[1/1] Processando PL 4381/2023...
  ✓ Senado: OK
  ✓ Câmara: OK
==================================================
SINCRONIZAÇÃO CONCLUÍDA
==================================================
Total de proposições: 1
Senado (sucessos): 1
Câmara (sucessos): 1
Erros: 0
Tempo total: 3.45 segundos
```

## API Endpoints

### Senado Activities
- **List**: `GET /api/atividades/senado/`
- **Detail**: `GET /api/atividades/senado/{id}/`
- **Filters**: `proposicao`, `data`, `colegiado_sigla`, `ente_administrativo_sigla`
- **Search**: `descricao`, `colegiado_nome`, `ente_administrativo_nome`

### Câmara Activities
- **List**: `GET /api/atividades/camara/`
- **Detail**: `GET /api/atividades/camara/{id}/`
- **Filters**: `proposicao`, `sigla_orgao`, `cod_tipo_tramitacao`, `ambito`
- **Search**: `despacho`, `descricao_tramitacao`, `descricao_situacao`

### Example API Response

```json
{
  "id": 1,
  "proposicao": 1,
  "id_informe": 2245882,
  "data": "2025-07-16",
  "descricao": "Autuado o Projeto de Lei nº 2583/2020, proveniente da Câmara dos Deputados.",
  "colegiado_sigla": "PLEN",
  "colegiado_nome": "Plenário do Senado Federal",
  "ente_administrativo_sigla": "SLSF",
  "ente_administrativo_nome": "Secretaria Legislativa do Senado Federal",
  "sigla_situacao_iniciada": "AGDESP",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

## Admin Interface

### SenadoActivityHistory Admin
- **List View**: Proposição, ID, Date, Committee, Administrative Entity, Status
- **Filters**: Date, Committee, Administrative Entity, Status
- **Search**: Proposição identifier, description, committee names
- **Date Hierarchy**: By activity date

### CamaraActivityHistory Admin
- **List View**: Proposição, Sequence, Date/Time, Organ, Procedure Type
- **Filters**: Date/Time, Organ, Procedure Type, Scope
- **Search**: Proposição identifier, dispatch, procedure descriptions
- **Date Hierarchy**: By activity date/time

## Data Sources

### Senado Federal API
- **Endpoint**: `/processo/{sf_id}`
- **Data Path**: `autuacoes[].informesLegislativos[]`
- **Exclusions**: `documentosAssociados` field is skipped
- **Rate Limit**: 10 requests per second

### Câmara dos Deputados API
- **Endpoint**: `/proposicoes/{cd_id}/tramitacoes`
- **Data Path**: `dados[]`
- **Rate Limit**: 15 requests per second

## Synchronization Logic

1. **Filter Proposições**: Only process proposições with `sf_id` or `cd_id`
2. **Senado Sync**: For proposições with `sf_id`, fetch process data and extract `informesLegislativos`
3. **Câmara Sync**: For proposições with `cd_id`, fetch tramitações data
4. **Upsert Logic**: Create new records or update existing ones based on unique identifiers
5. **Error Handling**: Log errors but continue processing other proposições

## Performance Considerations

- **Rate Limiting**: 1-second delay between proposições
- **Batch Processing**: Can limit number of proposições per run
- **Incremental Updates**: Existing records are updated rather than recreated
- **Error Recovery**: Failed syncs don't prevent others from processing

## Troubleshooting

### Common Issues

1. **No activities found**: Proposição may not have activity history in the API
2. **Partial sync**: Proposição may have activities in only one house
3. **API errors**: Check logs for specific error messages
4. **Rate limiting**: Service automatically handles delays

### Debug Commands

```bash
# Check activity counts
docker compose run --rm app python manage.py shell -c "from apps.pauta.models import SenadoActivityHistory, CamaraActivityHistory; print(f'Senado activities: {SenadoActivityHistory.objects.count()}'); print(f'Câmara activities: {CamaraActivityHistory.objects.count()}')"

# Test specific proposição
docker compose run --rm app python manage.py sync_activity_history --proposicao-id 1 --limit 1
```

## Integration with Main Sync

The Activity History sync is independent of the main proposição sync:
- Main sync populates `sf_id` and `cd_id` fields
- Activity History sync uses these IDs to fetch detailed activity data
- Both can be run independently or together

## Future Enhancements

Potential improvements for Activity History:
- **Real-time Updates**: Webhook integration for live updates
- **Activity Analytics**: Statistical analysis of procedural patterns
- **Timeline Visualization**: Graphical representation of legislative progress
- **Notification System**: Alerts for important procedural milestones
- **Data Export**: CSV/Excel export functionality
