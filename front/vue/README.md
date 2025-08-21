# Agenda União e Reconstrução - Frontend

Frontend SPA application for the Agenda União e Reconstrução project, built with Vue 3 and Vuetify.

## Features

- **Modern UI**: Built with Vuetify 3 for a beautiful, responsive interface
- **Summary Dashboard**: Displays eixos, temas, and proposições in an organized layout
- **Real-time Data**: Fetches data from Django backend APIs
- **Responsive Design**: Works on desktop and mobile devices

## Tech Stack

- Vue 3 (Composition API)
- Vuetify 3 (Material Design components)
- Axios (HTTP client)
- Vite (Build tool)

## Setup

1. Install dependencies:
```bash
npm install
```

2. Start development server:
```bash
npm run dev
```

3. Build for production:
```bash
npm run build
```

## API Configuration

The frontend connects to the Django backend via proxy configuration in `vite.config.js`. The API endpoints used are:

- `/api/bi/eixos/` - Eixos estratégicos
- `/api/bi/temas/` - Temas
- `/api/bi/proposicoes/` - Proposições

## Project Structure

```
src/
├── components/
│   └── AgendaLanding.vue    # Main landing page component
├── services/
│   └── api.js              # API service for data fetching
├── plugins/
│   └── vuetify.js          # Vuetify configuration
└── main.js                 # App entry point
```

## Development

The application is configured to run with the Django backend. Make sure the backend is running on `http://localhost:8000` before starting the frontend.

For development with Docker, use the provided Docker configuration in the root directory.


