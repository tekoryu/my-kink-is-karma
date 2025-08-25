# Architecture Overview

## Project Structure

```
meu_projeto/
├── backend/                 # Django backend application
│   ├── meu_app_django/     # Django project settings
│   ├── manage.py           # Django management script
│   └── requirements.txt    # Python dependencies
│
├── frontend/               # React frontend application
│   ├── public/            # Static files
│   ├── src/               # Source code
│   │   ├── assets/        # Images, fonts, etc.
│   │   ├── components/    # Reusable React components
│   │   └── pages/         # Page components
│   ├── package.json       # Node.js dependencies
│   └── README.md          # Frontend documentation
│
├── database/              # Database related files
│   ├── migrations/        # Database migrations
│   └── seeds/            # Database seed data
│
├── docs/                  # Project documentation
│   ├── 01_setup.md       # Setup instructions
│   ├── 02_architecture.md # This file
│   └── 03_api_endpoints.md # API documentation
│
├── .gitignore            # Git ignore rules
├── docker-compose.yml    # Docker configuration
├── LICENSE               # Project license
└── README.md             # Main project documentation
```

## Technology Stack

### Backend
- **Framework**: Django 4.2.7
- **API**: Django REST Framework
- **Database**: PostgreSQL (production), SQLite (development)
- **Authentication**: Django's built-in authentication system

### Frontend
- **Framework**: React 18.2.0
- **Build Tool**: Create React App
- **HTTP Client**: Axios
- **Styling**: CSS (can be extended with styled-components or other CSS-in-JS solutions)

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Database**: PostgreSQL 13
- **Development**: Hot reloading for both frontend and backend

## Data Flow

1. **Frontend** makes HTTP requests to the **Backend API**
2. **Backend** processes requests and interacts with the **Database**
3. **Backend** returns JSON responses to the **Frontend**
4. **Frontend** updates the UI based on the received data

## Security Considerations

- CORS configuration for frontend-backend communication
- Environment variables for sensitive configuration
- Django's built-in security features (CSRF protection, SQL injection prevention, etc.)
- Input validation on both frontend and backend
