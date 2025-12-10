from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.accounts.models import UserProfile
from apps.accounts.serializers import (
    UserSerializer, 
    UserProfileSerializer, 
    RegisterSerializer
)

User = get_user_model()

class UserSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='user@example.com',
            password='password',
            first_name='John',
            last_name='Doe',
            username='user'
        )

    def test_user_serialization(self):
        serializer = UserSerializer(self.user)
        data = serializer.data
        self.assertEqual(data['email'], 'user@example.com')
        self.assertEqual(data['first_name'], 'John')
        self.assertEqual(data['full_name'], 'John Doe')
        self.assertNotIn('password', data)


class UserProfileSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='profile@example.com', password='pw', username='profileuser')
        self.profile = UserProfile.objects.create(
            user=self.user,
            role='EMPLOYER',
            phone='1234567890'
        )

    def test_profile_serialization(self):
        serializer = UserProfileSerializer(self.profile)
        data = serializer.data
        self.assertEqual(data['role'], 'EMPLOYER')
        self.assertEqual(data['phone'], '1234567890')
        # Check nested user data
        self.assertEqual(data['user']['email'], 'profile@example.com')


class RegisterSerializerTest(TestCase):
    def test_validate_passwords_match(self):
        data = {
            'email': 'new@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'password123',
            'password2': 'password123',
            'role': 'EMPLOYEE'
        }
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())  # password too common

    def test_validate_passwords_mismatch(self):
        data = {
            'email': 'new@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'password123',
            'password2': 'mismatch',
            'role': 'EMPLOYEE'
        }
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)

    def test_create_user(self):
        data = {
            'email': 'create@example.com',
            'first_name': 'Create',
            'last_name': 'User',
            'password': 'password123****',
            'password2': 'password123****',
            'role': 'PROVIDER'
        }
        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        
        self.assertEqual(user.email, 'create@example.com')
        self.assertTrue(user.check_password('password123****'))
        self.assertTrue(UserProfile.objects.filter(user=user, role='PROVIDER').exists())
