from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import User
import requests
from django.conf import settings
import json

class KeycloakAuthentication(BaseAuthentication):
    """
    Custom authentication class for Keycloak JWT tokens
    """

    def authenticate(self, request):
        auth_header = get_authorization_header(request).decode('utf-8')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header.split(' ')[1]
        
        try:
            # Verify token with Keycloak
            response = requests.get(
                settings.OIDC_OP_USER_ENDPOINT,
                headers={
                    'Authorization': f'Bearer {token}'
                }
            )
            
            if response.status_code != 200:
                raise AuthenticationFailed('Invalid token or token expired')
            
            user_info = response.json()
            
            # Get or create the user
            try:
                user = User.objects.get(username=user_info['preferred_username'])
            except User.DoesNotExist:
                # Create a new user if they don't exist in Django but exist in Keycloak
                user = User.objects.create_user(
                    username=user_info['preferred_username'],
                    email=user_info.get('email', ''),
                )
            
            return (user, token)
        
        except Exception as e:
            raise AuthenticationFailed(f'Authentication error: {str(e)}')
        
    def authenticate_header(self, request):
        return 'Bearer' 