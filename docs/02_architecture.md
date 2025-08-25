# Architecture Overview

## Project Structure

```
my-kink-is-karma/           # Backend Django application
├── app/                   # Django project root
│   ├── apps/             # Django applications
│   │   ├── authentication/  # Authentication app
│   │   ├── core/         # Core functionality
│   │   └── pauta/        # Pauta (agenda) app
│   ├── config/           # Django project settings
│   └── manage.py         # Django management script
│
├── docs/                 # Project documentation
│   ├── 01_setup.md      # Setup instructions
│   ├── 02_architecture.md # This file
│   └── 03_api_endpoints.md # API documentation
│
├── scripts/             # Helper scripts
├── requirements.txt     # Python dependencies
├── compose.yaml         # Docker configuration
└── README.md           # Main project documentation

../fe_mykinkiskarma/     # Frontend Vue.js application (separate project)
├── vue/                # Vue application
│   ├── src/           # Source code
│   ├── public/        # Static files
│   └── package.json   # Node.js dependencies
└── Agenda Estratégica.pbix  # Power BI file
```

## Technology Stack

### Backend
- **Framework**: Django 4.2.7
- **API**: Django REST Framework
- **Database**: PostgreSQL (production), SQLite (development)
- **Authentication**: Django's built-in authentication system

### Frontend (Separate Project)
- **Framework**: Vue 3
- **Build Tool**: Vite
- **HTTP Client**: Axios  
- **Styling**: CSS + Vuetify
- **Location**: `../fe_mykinkiskarma/` (separate repository)

### Infrastructure
- **Containerization**: Docker & Docker Compose (backend only)
- **Database**: PostgreSQL 15
- **Development**: Hot reloading for backend; frontend runs independently

## Data Flow

1. **Frontend** (separate project) makes HTTP requests to the **Backend API**
2. **Backend** processes requests and interacts with the **Database**
3. **Backend** returns JSON responses to the **Frontend**
4. **Frontend** updates the UI based on the received data

Note: Frontend and backend are now separate projects with independent deployment cycles.

## Security Considerations

- CORS configuration for frontend-backend communication
- Environment variables for sensitive configuration
- Django's built-in security features (CSRF protection, SQL injection prevention, etc.)
- Input validation on both frontend and backend
