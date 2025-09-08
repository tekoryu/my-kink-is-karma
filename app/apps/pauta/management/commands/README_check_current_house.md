# Command: check_current_house

## Overview
Django management command to verify and update the `current_house` field for propositions based on their activity history. This is useful for maintenance tasks and ensuring data consistency.

## Purpose
The `current_house` field indicates which legislative house (Senado or Câmara) currently has a proposition. This command:
- Analyzes activity history from both houses
- Determines the correct current house based on the most recent activity
- Updates the field when necessary
- Provides detailed reporting and dry-run capabilities

## Usage

### Basic Commands

```bash
# Check and update all propositions
docker compose run --rm app python manage.py check_current_house

# Dry run (no changes made)
docker compose run --rm app python manage.py check_current_house --dry-run

# Process only first 50 propositions
docker compose run --rm app python manage.py check_current_house --limit 50

# Check specific proposition by ID
docker compose run --rm app python manage.py check_current_house --proposicao-id 123

# Show detailed information during processing
docker compose run --rm app python manage.py check_current_house --show-details
```

### Options

| Option | Description |
|--------|-------------|
| `--limit LIMIT` | Limit number of propositions to process |
| `--proposicao-id ID` | Process only a specific proposition by ID |
| `--dry-run` | Execute without making database changes |
| `--show-details` | Show detailed information about changes |

## How It Works

1. **Data Analysis**: For each proposition, the command:
   - Finds the most recent Senado activity (by date)
   - Finds the most recent Câmara activity (by datetime)
   - Compares dates to determine which house has the latest activity

2. **Logic**:
   - If both houses have activities → Use house with most recent activity
   - If only one house has activities → Use that house
   - If no activities → No change made to current_house

3. **Updates**: Only updates when the calculated value differs from stored value

## Output Examples

### Single Proposition Check
```
Verificando proposição específica: PL 1234/2023
Proposição PL 1234/2023: current_house atualizado de 'null' para 'SF'

PL 1234/2023:
  - current_house atual: SF
  - Atividades Senado: 15 (última: 2023-08-15)
  - Atividades Câmara: 8 (última: 2023-07-20)
  - Status: ✓ Correto (deveria ser SF)
```

### Batch Processing Summary
```
Total de proposições a processar: 100
Processando proposições...

============================================================
Processamento concluído:
  - Total processadas: 100
  - Atualizações realizadas: 12
  - Sem alteração: 88
```

### Dry Run Example
```
Total de proposições a processar: 3
Modo dry-run: não serão feitas alterações no banco
Mostrando status de 3 proposições:

PL 4384/2023:
  - current_house atual: null
  - Atividades Senado: 0 (última: None)
  - Atividades Câmara: 0 (última: None)
  - Status: ⚠ Sem atividades registradas
```

## Status Indicators

- ✓ **Correto**: current_house matches expected value
- ⚠ **Necessita atualização**: current_house differs from expected
- ⚠ **Sem atividades registradas**: No activity history found

## Use Cases

### 1. Regular Maintenance
```bash
# Weekly check for all propositions
docker compose run --rm app python manage.py check_current_house
```

### 2. Post-Migration Verification
```bash
# After data imports or migrations
docker compose run --rm app python manage.py check_current_house --show-details
```

### 3. Troubleshooting
```bash
# Check specific proposition reported as incorrect
docker compose run --rm app python manage.py check_current_house --proposicao-id 456 --show-details
```

### 4. Batch Updates
```bash
# Process in smaller batches for large datasets
docker compose run --rm app python manage.py check_current_house --limit 500
```

## Performance

The command includes performance logging and processes efficiently:
- Batch processing with progress indicators
- Database-optimized queries using aggregations
- Minimal memory footprint with queryset iteration
- Detailed performance metrics logged

## Integration with Automatic Updates

This command works alongside the automatic signal-based updates:
- **Automatic**: Django signals update current_house when activity history changes
- **Manual**: This command handles bulk corrections and verification
- **Complementary**: Both systems ensure data consistency

## Logging

All operations are logged with performance metrics including:
- Total propositions processed
- Number of updates made
- Processing duration
- Command options used
