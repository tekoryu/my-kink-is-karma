# Frontend (Vue 3 + Vite + Nginx)

This document describes the Vue.js frontend container, development and production workflows, environment variables, and Docker Compose usage.

## Overview

- Vue 3 SPA built with Vite
- Production: built assets served by Nginx inside the `frontend` container
- Development: optional hot-reload dev server using `Dockerfile.dev`
- Integrated with the Django API (`app` service)

## Project Structure

- `front/vue/` - Vue application root
  - `Dockerfile` - Production multi-stage build (Node build -> Nginx serve)
  - `Dockerfile.dev` - Development image (Node + Vite hot-reload)
  - `nginx.conf` - Nginx configuration for SPA routing and optional API proxy
  - `src/` - Vue source files
  - `public/` - Static public assets

## Docker Compose Service

The `frontend` service is defined in `compose.yaml`:

- Build context: `./front/vue`
- Production image: Nginx serving built `dist/`
- Healthcheck: HTTP check on container port 80
- Depends on `app` service health

## Environment Variables

Set these in `.env` (defaults are shown):

- `FRONTEND_PORT=8080` - Host port for the frontend
- `FRONTEND_CONTAINER_PORT=80` - Container port (Nginx)
- `NODE_ENV=production` - Build/runtime mode for the build stage
- `VITE_API_URL=http://localhost:8000` - API base URL exposed to the frontend at build/runtime
- `VITE_APP_TITLE=My Kink is Karma` - App title exposed to the frontend

Notes:
- If using Nginx proxy (see nginx.conf), you can set `VITE_API_URL=/api` and route to `app:8000` via Nginx.
- If calling Django directly from the browser, ensure CORS is configured in Django for the frontend origin.

## Quick Start (Production)

```bash
# Build and start only the frontend service
docker compose up --build frontend

# Access
# http://localhost:8080 (or the value of FRONTEND_PORT)
```

Logs:
```bash
docker compose logs -f frontend
```

## Development (Hot-Reload)

There are two supported approaches. The recommended approach is listed first.

### Option A (Recommended): Compose override using `Dockerfile.dev`

Create `compose.frontend.dev.yaml` with the following contents:

```yaml
services:
  frontend:
    build:
      context: ./front/vue
      dockerfile: Dockerfile.dev
    ports:
      - "5173:5173"
    volumes:
      - ./front/vue:/app
      - /app/node_modules
    environment:
      - VITE_API_URL=${VITE_API_URL:-http://localhost:8000}
      - VITE_APP_TITLE=${VITE_APP_TITLE:-My Kink is Karma}
    command: ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]
```

Run with both compose files:
```bash
docker compose -f compose.yaml -f compose.frontend.dev.yaml up --build frontend
# Access: http://localhost:5173
```

### Option B: Keep production container while developing

Use the production container for serving built assets and rebuild on changes:
```bash
# Rebuild on demand (no hot-reload)
docker compose up --build frontend
```

This mode is simpler but slower for iterative development.

## Nginx Configuration (Production)

- SPA routing (`try_files`) returns `index.html` for unknown routes
- Static assets are cached aggressively
- Optional `/api/` location proxies to the Django `app` service at `http://app:8000/`

If you proxy API calls through Nginx:
- Set `VITE_API_URL=/api` in `.env`
- Ensure Django `ALLOWED_HOSTS` includes the frontend host

## Package Scripts

The frontend includes useful scripts (run inside the dev container):

```bash
# Dev server (run by compose override)
npm run dev

# Production build
npm run build

# Lint (requires dev image)
npm run lint

# Type check (optional; requires dev image)
npm run type-check
```

Via Docker Compose (dev image):
```bash
# One-off lint
docker compose -f compose.yaml -f compose.frontend.dev.yaml run --rm frontend npm run lint

# One-off build (production image)
docker compose run --rm frontend sh -c "true"  # build happens during 'up' for production
```

## Integration with Backend

- Default direct API calls: `VITE_API_URL=http://localhost:8000`
- Via Nginx proxy: `VITE_API_URL=/api` with proxy to `app:8000`

Ensure Django CORS is configured if calling directly from the browser origin.

## Troubleshooting

- Frontend not reachable:
  - Verify port mapping (`FRONTEND_PORT` or `5173` for dev)
  - Check container logs: `docker compose logs -f frontend`
- API calls failing (CORS):
  - Use the Nginx `/api` proxy or enable CORS in Django
- Blank page on refresh with SPA routes:
  - Ensure `nginx.conf` includes `try_files $uri $uri/ /index.html;`

---

This README follows the repository patterns: concise docker-first commands, environment variable configuration, and clear dev/prod alternatives with a recommended approach.
