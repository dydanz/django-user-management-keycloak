import pytest
from django.test import TestCase
from users.tests.factories import UserFactory, UserProfileFactory
from users.models import UserProfile

class TestUserProfile(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.profile = self.user.userprofile

    def test_user_profile_creation(self):
        """Test that a UserProfile is automatically created when a User is created"""
        new_user = UserFactory()
        self.assertIsNotNone(new_user.userprofile)
        self.assertFalse(new_user.userprofile.mfa_enabled)
        self.assertIsNone(new_user.userprofile.keycloak_id)

    def test_user_profile_str_method(self):
        """Test the string representation of UserProfile"""
        expected_string = f"{self.user.username}'s profile"
        self.assertEqual(str(self.profile), expected_string)

    def test_user_profile_fields(self):
        """Test that UserProfile fields can be updated"""
        self.profile.mfa_enabled = True
        self.profile.phone_number = '+15550001234'
        self.profile.keycloak_id = 'test-keycloak-id'
        self.profile.save()

        updated_profile = self.user.userprofile
        self.assertTrue(updated_profile.mfa_enabled)
        self.assertEqual(updated_profile.phone_number, '+15550001234')
        self.assertEqual(updated_profile.keycloak_id, 'test-keycloak-id')

    def test_cascade_delete(self):
        """Test that UserProfile is deleted when User is deleted"""
        profile_id = self.profile.id
        self.user.delete()
        with self.assertRaises(UserProfile.DoesNotExist):
            UserProfile.objects.get(id=profile_id) 