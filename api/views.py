from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth import logout, authenticate
from django.core.mail import send_mail
from django.conf import settings
import logging
import random
import string
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import requests

# Initialize logger
logger = logging.getLogger(__name__)

# Security schema for protected endpoints
security_requirements = [{'Bearer': []}]

# Request and response schemas for Swagger
register_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['username', 'email', 'password'],
    properties={
        'username': openapi.Schema(type=openapi.TYPE_STRING),
        'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),
        'password': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_PASSWORD),
    }
)

forgot_password_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['email'],
    properties={
        'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),
    }
)

reset_password_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['email', 'token', 'new_password'],
    properties={
        'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),
        'token': openapi.Schema(type=openapi.TYPE_STRING),
        'new_password': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_PASSWORD),
    }
)

login_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['username', 'password'],
    properties={
        'username': openapi.Schema(type=openapi.TYPE_STRING),
        'password': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_PASSWORD),
    }
)

@swagger_auto_schema(
    method='post',
    request_body=register_schema,
    responses={
        201: openapi.Response('User created successfully', schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'message': openapi.Schema(type=openapi.TYPE_STRING),
            }
        )),
        400: openapi.Response('Bad request', schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'error': openapi.Schema(type=openapi.TYPE_STRING),
            }
        )),
    },
    operation_description="Register a new user account",
    operation_summary="User Registration",
    tags=['Authentication']
)
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')

    if not all([username, email, password]):
        logger.error("Registration failed: Missing fields")
        return Response({'error': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        logger.error(f"Registration failed: Username {username} already exists")
        return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(email=email).exists():
        logger.error(f"Registration failed: Email {email} already exists")
        return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)

    # Register user in Keycloak
    try:
        # Get admin token from Keycloak
        admin_token_response = requests.post(
            f"{settings.KEYCLOAK_URL}/realms/master/protocol/openid-connect/token",
            data={
                'grant_type': 'password',
                'client_id': 'admin-cli',
                'username': 'admin',
                'password': 'admin',
            },
            headers={
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        )
        logger.debug(f"Admin token response: {admin_token_response.status_code} - {admin_token_response.text}")

        if admin_token_response.status_code != 200:
            logger.error("Failed to authenticate with Keycloak admin")
            return Response({'error': 'Failed to authenticate with Keycloak admin'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        admin_token = admin_token_response.json()['access_token']
        
        # Create user in Keycloak
        create_user_response = requests.post(
            f"{settings.KEYCLOAK_URL}/admin/realms/{settings.KEYCLOAK_REALM}/users",
            json={
                'username': username,
                'email': email,
                'enabled': True,
                'emailVerified': True,
                'credentials': [
                    {
                        'type': 'password',
                        'value': password,
                        'temporary': False
                    }
                ]
            },
            headers={
                'Authorization': f'Bearer {admin_token}',
                'Content-Type': 'application/json'
            }
        )

        if create_user_response.status_code != 201:
            logger.error(f"Failed to create user in Keycloak: {create_user_response.text}")
            return Response({'error': 'Failed to create user in Keycloak'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Get the created user's ID from Keycloak
        user_id_response = requests.get(
            f"{settings.KEYCLOAK_URL}/admin/realms/{settings.KEYCLOAK_REALM}/users",
            params={'username': username},
            headers={
                'Authorization': f'Bearer {admin_token}',
                'Content-Type': 'application/json'
            }
        )

        if user_id_response.status_code != 200:
            logger.error(f"Failed to get user ID from Keycloak: {user_id_response.text}")
            return Response({'error': 'Failed to get user ID from Keycloak'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        keycloak_users = user_id_response.json()
        if not keycloak_users:
            logger.error("User not found in Keycloak after creation")
            return Response({'error': 'User not found in Keycloak after creation'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        keycloak_id = keycloak_users[0]['id']

        # Create user in Django with the Keycloak ID
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        
        # Update the user's profile with the Keycloak ID
        user.userprofile.keycloak_id = keycloak_id
        user.userprofile.save()

        logger.info(f"User {username} created successfully with Keycloak ID: {keycloak_id}")
        return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({'error': f'Registration error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@swagger_auto_schema(
    method='post',
    responses={200: 'Successfully logged out'},
    operation_description="Logout the current user",
    operation_summary="User Logout",
    tags=['Authentication'],
    security=security_requirements,
    manual_parameters=[
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description='Bearer <token>',
            type=openapi.TYPE_STRING,
            required=True
        )
    ]
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    logout(request)
    return Response({'message': 'Successfully logged out'})

@swagger_auto_schema(
    method='post',
    request_body=forgot_password_schema,
    responses={
        200: 'Password reset email sent',
        400: 'Email is required',
        404: 'User not found'
    },
    operation_description="Request password reset email",
    operation_summary="Forgot Password",
    tags=['Authentication']
)
@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    email = request.data.get('email')
    if not email:
        return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
        # Generate a random token
        token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
        # Store token in session or cache
        request.session[f'reset_token_{email}'] = token
        
        # Send email with reset link
        reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}&email={email}"
        send_mail(
            'Password Reset Request',
            f'Click the following link to reset your password: {reset_link}',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        return Response({'message': 'Password reset email sent'})
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

@swagger_auto_schema(
    method='post',
    request_body=reset_password_schema,
    responses={
        200: 'Password reset successful',
        400: 'Invalid request',
        404: 'User not found'
    },
    operation_description="Reset password using token from email",
    operation_summary="Reset Password",
    tags=['Authentication']
)
@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    email = request.data.get('email')
    token = request.data.get('token')
    new_password = request.data.get('new_password')

    if not all([email, token, new_password]):
        return Response({'error': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)

    stored_token = request.session.get(f'reset_token_{email}')
    if not stored_token or stored_token != token:
        return Response({'error': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
        user.set_password(new_password)
        user.save()
        # Remove the token from session
        del request.session[f'reset_token_{email}']
        return Response({'message': 'Password reset successful'})
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

@swagger_auto_schema(
    method='post',
    request_body=login_schema,
    responses={
        200: openapi.Response('Login successful', schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'token': openapi.Schema(type=openapi.TYPE_STRING),
                'refresh_token': openapi.Schema(type=openapi.TYPE_STRING),
            }
        )),
        400: openapi.Response('Bad request', schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'error': openapi.Schema(type=openapi.TYPE_STRING),
            }
        )),
        401: openapi.Response('Authentication failed', schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'error': openapi.Schema(type=openapi.TYPE_STRING),
            }
        )),
    },
    operation_description="Login using Keycloak credentials",
    operation_summary="User Login",
    tags=['Authentication']
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    logger.debug(f"Login attempt for user: {username}")

    if not all([username, password]):
        logger.error("Login failed: Missing fields")
        return Response({'error': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)

    # Get token from Keycloak
    try:
        response = requests.post(
            settings.OIDC_OP_TOKEN_ENDPOINT,
            data={
                'grant_type': 'password',
                'client_id': settings.OIDC_RP_CLIENT_ID,
                'client_secret': settings.OIDC_RP_CLIENT_SECRET,
                'username': username,
                'password': password,
            },
            headers={
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        )
        
        if response.status_code != 200:
            logger.error(f"Login failed: {response.status_code} - {response.text}")
            if response.status_code == 401:
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response({'error': 'Authentication failed'}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'error': 'Authentication failed'}, status=status.HTTP_401_UNAUTHORIZED)
        
        token_data = response.json()
        logger.info(f"User {username} logged in successfully")
        return Response({
            'token': token_data['access_token'],
            'refresh_token': token_data.get('refresh_token'),
        })
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return Response({'error': f'Authentication error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@swagger_auto_schema(
    method='get',
    responses={200: 'Keycloak configuration status'},
    operation_description="Check Keycloak configuration",
    operation_summary="Keycloak Health Check",
    tags=['System'],
    security=security_requirements,
    manual_parameters=[
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description='Bearer <token>',
            type=openapi.TYPE_STRING,
            required=True
        )
    ]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def keycloak_check(request):
    """Check Keycloak configuration"""
    try:
        # Test connection to Keycloak server
        server_response = requests.get(
            f"{settings.KEYCLOAK_URL}/realms/{settings.KEYCLOAK_REALM}/.well-known/openid-configuration"
        )
        
        # Test admin authentication
        admin_token_response = requests.post(
            f"{settings.KEYCLOAK_URL}/realms/master/protocol/openid-connect/token",
            data={
                'grant_type': 'password',
                'client_id': 'admin-cli',
                'username': 'admin',
                'password': 'admin',
            },
            headers={
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        )
        
        # Try to get client info
        client_info = None
        if admin_token_response.status_code == 200:
            admin_token = admin_token_response.json()['access_token']
            client_response = requests.get(
                f"{settings.KEYCLOAK_URL}/admin/realms/{settings.KEYCLOAK_REALM}/clients",
                headers={
                    'Authorization': f'Bearer {admin_token}'
                }
            )
            client_info = client_response.json() if client_response.status_code == 200 else None
        
        return Response({
            'keycloak_server': {
                'status': server_response.status_code,
                'message': 'Connected' if server_response.status_code == 200 else 'Failed'
            },
            'admin_auth': {
                'status': admin_token_response.status_code,
                'message': 'Authenticated' if admin_token_response.status_code == 200 else 'Failed'
            },
            'client_info': {
                'status': 'Available' if client_info else 'Not available',
                'clients': client_info
            },
            'configuration': {
                'keycloak_url': settings.KEYCLOAK_URL,
                'realm': settings.KEYCLOAK_REALM,
                'client_id': settings.OIDC_RP_CLIENT_ID,
            }
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@swagger_auto_schema(
    method='post',
    responses={
        200: 'Admin check successful',
        401: 'Authentication failed'
    },
    operation_description="Check admin credentials",
    operation_summary="Admin Check",
    tags=['System'],
    security=security_requirements,
    manual_parameters=[
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description='Bearer <token>',
            type=openapi.TYPE_STRING,
            required=True
        )
    ]
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def admin_check(request):
    """Check admin login credentials without Keycloak"""
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not all([username, password]):
        return Response({'error': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)
    
    user = authenticate(request, username=username, password=password)
    
    if user and user.is_active and user.is_superuser:
        return Response({
            'success': True,
            'username': username,
            'is_superuser': user.is_superuser,
            'auth_backend': user.backend if hasattr(user, 'backend') else None
        })
    else:
        return Response({
            'success': False,
            'message': 'Invalid credentials or user is not a superuser'
        }, status=status.HTTP_401_UNAUTHORIZED)