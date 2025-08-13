#!/usr/bin/env pwsh
# -*- coding: utf-8 -*-

# Activate virtual environment and run Django dumpdata command
docker compose run --rm app sh -c "python manage.py dumpdata --all --indent 4 > ./apps/core/fixtures/data_dump.json"