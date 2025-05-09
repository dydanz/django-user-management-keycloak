import pytest
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from users.tests.factories import UserFactory, UserProfileFactory

class TestUserViews(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.profile = self.user.userprofile
        self.client.force_authenticate(user=self.user)

    # def test_profile_view(self):
    #     """Test the profile view template rendering"""
    #     response = self.client.get(reverse('profile'))
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertTemplateUsed(response, 'users/profile.html')

    def test_get_user_profile_authenticated(self):
        """Test getting user profile when authenticated"""
        response = self.client.get(reverse('api_profile'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user.username)
        self.assertEqual(response.data['email'], self.user.email)
        self.assertEqual(response.data['mfa_enabled'], self.profile.mfa_enabled)
        self.assertEqual(response.data['phone_number'], self.profile.phone_number)

    def test_get_user_profile_unauthenticated(self):
        """Test getting user profile when not authenticated"""
        self.client.force_authenticate(user=None)
        response = self.client.get(reverse('api_profile'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_toggle_mfa_authenticated(self):
        """Test toggling MFA when authenticated"""
        initial_mfa_status = self.profile.mfa_enabled
        response = self.client.post(reverse('toggle_mfa'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.profile.refresh_from_db()
        self.assertNotEqual(initial_mfa_status, self.profile.mfa_enabled)
        self.assertEqual(response.data['mfa_enabled'], self.profile.mfa_enabled)

    def test_toggle_mfa_unauthenticated(self):
        """Test toggling MFA when not authenticated"""
        self.client.force_authenticate(user=None)
        response = self.client.post(reverse('toggle_mfa'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_phone_authenticated(self):
        """Test updating phone number when authenticated"""
        new_phone = '+15550009999'
        response = self.client.post(
            reverse('update_phone'),
            {'phone_number': new_phone},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.phone_number, new_phone)
        self.assertEqual(response.data['phone_number'], new_phone)

    def test_update_phone_missing_number(self):
        """Test updating phone number with missing data"""
        response = self.client.post(
            reverse('update_phone'),
            {},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_phone_unauthenticated(self):
        """Test updating phone number when not authenticated"""
        self.client.force_authenticate(user=None)
        response = self.client.post(
            reverse('update_phone'),
            {'phone_number': '+15550009999'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN) 