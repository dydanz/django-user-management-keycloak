from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import UserProfile
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Security schema for protected endpoints
security_requirements = [{'Bearer': []}]

# Authorization parameter for protected endpoints
bearer_auth = openapi.Parameter(
    'Authorization',
    openapi.IN_HEADER,
    description='Bearer <token>',
    type=openapi.TYPE_STRING,
    required=True
)

def profile_view(request):
    return render(request, 'users/profile.html')

@swagger_auto_schema(
    method='get',
    responses={
        200: openapi.Response(
            description='User profile retrieved successfully',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'username': openapi.Schema(type=openapi.TYPE_STRING),
                    'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),
                    'mfa_enabled': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'phone_number': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )
        ),
        401: 'Authentication failed',
        403: 'Permission denied'
    },
    operation_description="Get the current user's profile information",
    operation_summary="Get User Profile",
    tags=['User Profile'],
    security=security_requirements,
    manual_parameters=[bearer_auth]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    try:
        profile = request.user.userprofile
        return Response({
            'username': request.user.username,
            'email': request.user.email,
            'mfa_enabled': profile.mfa_enabled,
            'phone_number': profile.phone_number,
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@swagger_auto_schema(
    method='post',
    responses={
        200: openapi.Response(
            description='MFA status toggled successfully',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'mfa_enabled': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                }
            )
        ),
        401: 'Authentication failed'
    },
    operation_description="Toggle Multi-Factor Authentication (MFA) for the current user",
    operation_summary="Toggle MFA",
    tags=['User Profile'],
    security=security_requirements,
    manual_parameters=[bearer_auth]
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_mfa(request):
    profile = request.user.userprofile
    profile.mfa_enabled = not profile.mfa_enabled
    profile.save()
    return Response({'mfa_enabled': profile.mfa_enabled})

@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['phone_number'],
        properties={
            'phone_number': openapi.Schema(type=openapi.TYPE_STRING),
        }
    ),
    responses={
        200: openapi.Response(
            description='Phone number updated successfully',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'phone_number': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )
        ),
        400: 'Phone number is required',
        401: 'Authentication failed'
    },
    operation_description="Update the phone number for the current user",
    operation_summary="Update Phone Number",
    tags=['User Profile'],
    security=security_requirements,
    manual_parameters=[bearer_auth]
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_phone(request):
    phone_number = request.data.get('phone_number')
    if not phone_number:
        return Response({'error': 'Phone number is required'}, status=400)
    
    profile = request.user.userprofile
    profile.phone_number = phone_number
    profile.save()
    return Response({'phone_number': profile.phone_number})