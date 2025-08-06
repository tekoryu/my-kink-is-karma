#!/bin/sh
docker compose down -v --remove-orphans
docker prune -a -v
docker system prune -a -f
docker compose up --build
docker compose run --rm app sh -c "python manage.py createsuperuser --noinput"
Start-Process "http://localhost:8000"