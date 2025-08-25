# Docker Setup for Django + DRF + PostgreSQL

This project is configured to run with Docker and Docker Compose, providing a complete development environment with Django, Django REST Framework, and PostgreSQL.

## Project Structure

- `app/` - Django project root (mapped into the container at `/app`)
  - `apps/` - Container folder for Django applications
    - `authentication/` - Authentication app
    - `management/` - Django management commands
  - `config/` - Django project configuration
  - `manage.py` - Django management script
- `requirements.txt` - Python dependencies
- `requirements.dev.txt` - Dev-only dependencies (installed when DEV=true)
- `Dockerfile` - Docker image configuration
- `compose.yaml` - Docker services orchestration
- `scripts/` - Container startup scripts

## Prerequisites

- Docker
- Docker Compose (v2; use `docker compose ...`)

## Quick Start

1. Create an environment variables file `.env` at the repo root:
   ```bash
   # Example .env (adjust values as needed)
   DEBUG=True
   SECRET_KEY=your-secret-key-here

   DB_NAME=mykinkiskarma
   DB_USER=postgres
   DB_PASSWORD=postgres
   DB_HOST=db
   DB_PORT=5432

   ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

   # Optional: install dev dependencies at build-time
   DEV=true

   # Optional: auto-create superuser on startup if the entrypoint supports it
   DJANGO_SUPERUSER_USERNAME=admin
   DJANGO_SUPERUSER_EMAIL=admin@example.com
   DJANGO_SUPERUSER_PASSWORD=adminpass

   # Optional: explicit static/media roots if used by settings
   STATIC_ROOT=/vol/web/static
   MEDIA_ROOT=/vol/web/media
   ```

2. Build and start the services:
   ```bash
   docker compose up --build
   ```

3. Create a superuser (if not auto-created via env vars):
   ```bash
   docker compose exec app python manage.py createsuperuser
   ```

4. Access the application:
   - App: http://localhost:8000/
   - Django Admin: http://localhost:8000/admin/
   - Healthcheck: http://localhost:8000/health/

## Services

- app: Django application (port 8000)
- db: PostgreSQL database (port 5432)

The app service waits for the database to become healthy before starting.

## Environment Variables

Defined in `.env` and passed into containers:

- `DEBUG`: Django debug mode
- `SECRET_KEY`: Django secret key
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`: Database configuration
- `DEV`: When `true`, dev dependencies are installed at build time
- `STATIC_ROOT`, `MEDIA_ROOT`: Paths for static/media files (defaults are commonly `/vol/web/static` and `/vol/web/media`)
- `DJANGO_SUPERUSER_USERNAME`, `DJANGO_SUPERUSER_EMAIL`, `DJANGO_SUPERUSER_PASSWORD`: Auto-create superuser on startup (if supported by the entrypoint script)

## Volumes and Paths

- `./app` is mounted to `/app` (live code reload without rebuilding)
- Named volumes:
  - `static_volume` mapped to `/vol/web/static`
  - `media_volume` mapped to `/vol/web/media`

## Useful Commands
```aiignore
# Start services in background
docker compose up -d
# View logs (service only)
docker compose logs -f app
# Stop and remove containers (keep volumes)
docker compose down
# Stop and remove containers AND volumes (resets DB/static/media)
docker compose down -v
# Open a shell in the app container
docker compose exec app sh
# Django management (WORKDIR is /app; no need to cd)
docker compose exec app python manage.py migrate 
docker compose exec app python manage.py collectstatic --noinput 
docker compose exec app python manage.py createsuperuser 
docker compose exec app python manage.py shell 
docker compose exec app python manage.py test
# Run sync (most common operations)
docker compose exec app python manage.py sync_proposicoes 
docker compose exec app python manage.py sync_proposicoes --limit 10 
docker compose exec app python manage.py sync_proposicoes --proposicao-id 123 
docker compose exec app python manage.py sync_proposicoes --force 
docker compose exec app python manage.py sync_proposicoes --dry-run --limit 5
# Database access (uses .env values)
docker compose exec db psql -U "DB_USER" -d "DB_NAME"
# Healthcheck
curl -f http://localhost:8000/health/
```



## Development

- Code changes in `./app` are reflected immediately inside the container (`/app`) thanks to the bind mount.
- Set `DEV=true` (in `.env` or inline during build) to install development dependencies from `requirements.dev.txt`.

## Production

For production deployment:

1. Set `DEBUG=False`
2. Use a strong `SECRET_KEY`
3. Configure `ALLOWED_HOSTS` appropriately
4. Use secure, environment-specific DB credentials
5. Ensure static files are collected (`collectstatic`) and served by a web server or CDN
6. Consider a reverse proxy (e.g., Nginx) in front of the app service
7. Persist and back up the database volume

## Troubleshooting

- Database connection issues:
  - Ensure the `db` service is healthy: `docker compose ps`
  - Verify `.env` credentials match the DB container env
- Logs:
  - App logs: `docker compose logs -f app`
  - DB logs: `docker compose logs -f db`
- Healthcheck failures:
  - Confirm the app is reachable at `/health/`
  - Inspect container: `docker compose exec app sh`
- Static files:
  - If static files are missing, run `docker compose exec app python manage.py collectstatic --noinput`
- Reset environment:
  - `docker compose down -v` to remove containers and volumes (warning: this clears DB/static/media)