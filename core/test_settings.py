from core.settings import *

# Use SQLite for testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Add the app templates directory
TEMPLATES[0]['DIRS'].append(os.path.join(BASE_DIR, 'users/templates'))

# Use a simpler password hasher for testing
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable CSRF for testing API endpoints
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# Test-specific environment variables
KEYCLOAK_URL = 'http://localhost:8080'
KEYCLOAK_REALM = 'test-realm'
OIDC_RP_CLIENT_ID = 'test-client' 