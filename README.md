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
- `jq` command-line tool (required for Keycloak setup script)
  - On macOS: `brew install jq`
  - On Ubuntu/Debian: `apt-get install jq`
  - On CentOS/RHEL: `yum install jq`
- Basic understanding of containerized applications

## Quick Start

1. Clone the repository:
```bash
git clone <repository-url>
cd django-user-management-keycloak
```

2. Set permissions for scripts:
```bash
chmod +x setup.sh entrypoint.sh init-db.sh setup-keycloak.sh
```

3. Build and start the containers:
```bash
docker-compose up --build -d
```

4. Wait for all services to start up (this may take a minute or two).

5. Run the Keycloak setup script:
```bash
./setup-keycloak.sh
```

6. Access the application services:
   - Django Admin: http://localhost:8000/admin/ (username: admin, password: admin)
   - Keycloak Admin: http://localhost:8080/admin/ (username: admin, password: admin)
   - Frontend: http://localhost:3000
   - PostgreSQL: localhost:5434 (accessible with external tools)

## Detailed Setup Instructions

### Project Structure
The project follows a monorepo structure:
- `/` - Django backend (root directory)
- `/frontend` - React frontend
- Docker configuration files in the root directory

### Container Services
The application consists of the following services:
- **web**: Django application
- **db**: PostgreSQL database
- **redis**: Redis for caching/session management
- **keycloak**: Keycloak for authentication and authorization
- **frontend**: React.js application

### Database Setup
The application uses PostgreSQL, and the database is automatically initialized with:
- Main application database (`postgres`)
- Keycloak database (`keycloak`)

### Migrations
Django migrations are applied automatically during container startup. If you need to run them manually:
```bash
docker-compose exec web python manage.py migrate
```

### Creating a Superuser
A superuser is created automatically with the credentials specified in the environment variables:
- Username: admin
- Email: admin@example.com
- Password: admin

### Keycloak Configuration
The setup script (`setup-keycloak.sh`) automatically configures Keycloak with:
- A new realm: `django-app`
- A client: `django-client`
- Roles: `admin` and `user`
- A test user: `testuser` (password: `testuser`)

## Troubleshooting

### Port Conflicts
If you encounter port conflicts during startup:
- PostgreSQL is configured to use port 5434 on the host (mapped to 5432 in the container)
- If PostgreSQL port is still in use, edit the `docker-compose.yml` file to change the port mapping

### Database Issues
If Keycloak fails to connect to the database:
```bash
docker-compose exec db psql -U postgres -c "CREATE DATABASE keycloak;"
```

### Django Migrations
If Django fails due to migration issues:
```bash
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
```

### Keycloak Not Starting
Check if the Keycloak database was created properly:
```bash
docker-compose logs keycloak
```

If it shows database connection errors, ensure the `init-db.sh` script was executed:
```bash
docker-compose exec db cat /docker-entrypoint-initdb.d/init-db.sh
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

## Development Workflow

### Backend Development
```bash
# Start all services
docker-compose up -d

# View logs for a specific service
docker-compose logs -f web

# Run Django management commands
docker-compose exec web python manage.py <command>

# Apply migrations after model changes
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
```

### Frontend Development
```bash
# Start only the frontend service
docker-compose up -d frontend

# View frontend logs
docker-compose logs -f frontend

# Install new npm packages
docker-compose exec frontend npm install <package-name>
```

## Security Considerations

- All sensitive data is stored in environment variables
- Passwords are hashed using Django's built-in password hashing
- CSRF protection is enabled
- CORS is configured for development and production
- Session management is handled by Redis
- JWT tokens are used for API authentication
- MFA is available for additional security
- Keycloak provides robust authentication and authorization

## License

This project is licensed under the MIT License - see the LICENSE file for details. 