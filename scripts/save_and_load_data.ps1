#!/usr/bin/env pwsh
# -*- coding: utf-8 -*-

# Activate virtual environment and run Django dumpdata command
docker compose run --rm app sh -c "python manage.py dumpdata app.Proposicao app.Eixo app.Tema --indent 4 > ./apps/pauta/fixtures/data_dump.json"

# Load data
docker compose run --rm app sh -c "python manage.py loaddata ./apps/pauta/fixtures/data_dump.json"
