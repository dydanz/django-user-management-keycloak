from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import UserProfile

@login_required
def profile_view(request):
    return render(request, 'users/profile.html')

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    profile = request.user.userprofile
    return Response({
        'username': request.user.username,
        'email': request.user.email,
        'mfa_enabled': profile.mfa_enabled,
        'phone_number': profile.phone_number,
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_mfa(request):
    profile = request.user.userprofile
    profile.mfa_enabled = not profile.mfa_enabled
    profile.save()
    return Response({'mfa_enabled': profile.mfa_enabled})

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