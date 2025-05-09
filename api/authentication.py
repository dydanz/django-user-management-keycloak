from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import User
import requests
from django.conf import settings
import json
import logging

# Initialize logger
logger = logging.getLogger(__name__)

class KeycloakAuthentication(BaseAuthentication):
    """
    Custom authentication class for Keycloak JWT tokens
    """

    def authenticate(self, request):
        auth_header = get_authorization_header(request).decode('utf-8')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            logger.debug("No Bearer token found in request")
            return None
        
        token = auth_header.split(' ')[1]
        logger.debug("Verifying token with Keycloak")
        print(f"Verifying token with Keycloak")  # Debugging line to print the token
        
        try:
            # Verify token with Keycloak
            response = requests.get(
                settings.OIDC_OP_USER_ENDPOINT,
                headers={
                    'Authorization': f'Bearer {token}'
                }
            )
            
            logger.debug(f"Keycloak response status: {response.status_code}")
            if response.status_code != 200:
                logger.error(f"Token verification failed: {response.text}")
                raise AuthenticationFailed('Invalid token or token expired')
            
            user_info = response.json()
            logger.debug(f"User info received: {user_info.get('preferred_username')}")
            
            # Get or create the user
            try:
                user = User.objects.get(username=user_info['preferred_username'])
                logger.debug(f"Found existing user: {user.username}")
            except User.DoesNotExist:
                # Create a new user if they don't exist in Django but exist in Keycloak
                logger.debug(f"Creating new user: {user_info['preferred_username']}")
                user = User.objects.create_user(
                    username=user_info['preferred_username'],
                    email=user_info.get('email', ''),
                )
            
            return (user, token)
        
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            raise AuthenticationFailed(f'Authentication error: {str(e)}')
        
    def authenticate_header(self, request):
        return 'Bearer'