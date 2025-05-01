# Django User Management with Keycloak

A full-stack monolithic application for user management with Django backend and React frontend, using Keycloak for authentication and authorization.

## Features

- User Registration and Login
- Password-based and Social Login (Google, Facebook)
- Multi-factor Authentication (MFA)
- Role-Based Access Control (RBAC)
- Group-based Access Management
- Single Sign-On (SSO)
- Token Expiration Policy Management
- Session Clustering
- Forgot Password Flow
- User Profile Management

## Tech Stack

### Backend
- Django 5.0.2
- Django REST Framework
- PostgreSQL
- Redis
- Keycloak

### Frontend
- React.js
- Material-UI
- Axios

## Prerequisites

- Docker and Docker Compose
- Node.js 16+ (for local frontend development)
- Python 3.11+ (for local backend development)

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd django-user-management-keycloak
```

2. Create a `.env` file in the root directory with the following content:
```env
DEBUG=1
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgres://postgres:postgres@db:5432/postgres

# Redis
REDIS_URL=redis://redis:6379/0

# Keycloak
KEYCLOAK_URL=http://localhost:8080
KEYCLOAK_REALM=django-app
KEYCLOAK_CLIENT_ID=django-client
KEYCLOAK_CLIENT_SECRET=your-client-secret

# Django Admin
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=admin
```

3. Build and start the containers:
```bash
docker-compose up --build
```

4. Initialize the database and create a superuser:
```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

5. Access the applications:
- Django Admin: http://localhost:8000/admin
- Keycloak Admin: http://localhost:8080
- Frontend: http://localhost:3000

## Keycloak Setup

1. Access Keycloak Admin Console at http://localhost:8080
2. Login with admin/admin
3. Create a new realm named "django-app"
4. Create a new client:
   - Client ID: django-client
   - Client Protocol: openid-connect
   - Access Type: confidential
   - Valid Redirect URIs: http://localhost:3000/*
   - Web Origins: http://localhost:3000

5. Create roles:
   - admin
   - user

6. Create test users with appropriate roles

## Development

### Backend Development
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start development server
python manage.py runserver
```

### Frontend Development
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

## Testing

### Backend Tests
```bash
python manage.py test
```

### Frontend Tests
```bash
cd frontend
npm test
```

## API Endpoints

- POST /api/register/ - User registration
- POST /api/login/ - User login
- POST /api/logout/ - User logout
- POST /api/forgot-password/ - Request password reset
- POST /api/reset-password/ - Reset password
- GET /api/profile/ - Get user profile
- POST /api/toggle-mfa/ - Toggle MFA
- POST /api/update-phone/ - Update phone number

## Security Considerations

- All sensitive data is stored in environment variables
- Passwords are hashed using Django's built-in password hashing
- CSRF protection is enabled
- CORS is configured for development and production
- Session management is handled by Redis
- JWT tokens are used for API authentication
- MFA is available for additional security

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 