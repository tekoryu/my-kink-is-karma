# Docker Setup for Django + DRF + PostgreSQL

This project is configured to run with Docker and Docker Compose, providing a complete development environment with Django, Django REST Framework, and PostgreSQL.

## Project Structure

- `app/` - Django project root
  - `apps/` - Container folder for Django applications
    - `authentication/` - Authentication app
    - `management/` - Django management commands
  - `config/` - Django project configuration
  - `manage.py` - Django management script
- `requirements.txt` - Python dependencies
- `Dockerfile` - Docker image configuration
- `compose.yaml` - Docker services orchestration

## Prerequisites

- Docker
- Docker Compose

## Quick Start

1. **Create environment variables file:**
   ```bash
   # Create a .env file with your environment variables
   # Example:
   # DEBUG=True
   # SECRET_KEY=your-secret-key-here
   # DB_NAME=mykinkiskarma
   # DB_USER=postgres
   # DB_PASSWORD=postgres
   # ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
   ```

2. **Build and start the services:**
   ```bash
   docker compose up --build
   ```

3. **Create a superuser (in a new terminal):**
   ```bash
   docker compose exec web sh -c "cd app && python manage.py createsuperuser"
   ```

4. **Access the application:**
   - Django Admin: http://localhost:8000/admin/
   - API: http://localhost:8000/api/

## Services

- **Web (Django)**: Runs on port 8000
- **Database (PostgreSQL)**: Runs on port 5432

## Environment Variables

The application uses the following environment variables (defined in your `.env` file):

- `DEBUG`: Django debug mode
- `SECRET_KEY`: Django secret key
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `DB_NAME`: PostgreSQL database name
- `DB_USER`: PostgreSQL username
- `DB_PASSWORD`: PostgreSQL password
- `DB_HOST`: PostgreSQL host
- `DB_PORT`: PostgreSQL port

## Useful Commands

```bash
# Start services in background
docker compose up -d

# View logs
docker compose logs -f

# Stop services
docker compose down

# Rebuild and start
docker compose up --build

# Run Django management commands
docker compose exec web sh -c "cd app && python manage.py migrate"
docker compose exec web sh -c "cd app && python manage.py collectstatic"
docker compose exec web sh -c "cd app && python manage.py createsuperuser"

# Access Django shell
docker compose exec web sh -c "cd app && python manage.py shell"

# Access PostgreSQL
docker compose exec db psql -U postgres -d mykinkiskarma
```

## Development

The application code is mounted as a volume, so changes to your code will be reflected immediately without rebuilding the container.

## Production

For production deployment:

1. Set `DEBUG=False` in your environment variables
2. Use a proper `SECRET_KEY`
3. Configure proper `ALLOWED_HOSTS`
4. Use environment-specific database credentials
5. Consider using a reverse proxy (nginx) in front of the application

## Troubleshooting

- If the database connection fails, ensure PostgreSQL is running and healthy
- Check logs with `docker compose logs`
- The application waits for the database to be ready before starting
- Static files are collected automatically on startup 