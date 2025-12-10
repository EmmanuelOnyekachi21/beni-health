from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from apps.accounts.models import UserProfile

User = get_user_model()

class RegisterViewTest(APITestCase):
    def setUp(self):
        self.url = reverse('register')
        self.valid_payload = {
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'password123####',
            'password2': 'password123####',
            'role': 'EMPLOYEE'
        }

    def test_register_success(self):
        response = self.client.post(self.url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(UserProfile.objects.count(), 1)
        self.assertEqual(User.objects.get().email, 'newuser@example.com')

    def test_register_password_mismatch(self):
        payload = self.valid_payload.copy()
        payload['password2'] = 'mismatch'
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_register_duplicate_email(self):
        User.objects.create_user(
            email='newuser@example.com', 
            password='oldpassword', 
            username='olduser'
        )
        response = self.client.post(self.url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)


class LoginViewTest(APITestCase):
    def setUp(self):
        self.url = reverse('login')
        self.email = 'login@example.com'
        self.password = 'password123'
        self.user = User.objects.create_user(
            email=self.email, 
            password=self.password,
            username='loginuser'
        )
        UserProfile.objects.create(user=self.user, role='EMPLOYEE')

    def test_login_success(self):
        data = {
            'email': self.email,
            'password': self.password
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)

    def test_login_invalid_credentials(self):
        data = {
            'email': self.email,
            'password': 'wrongpassword'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserProfileViewTest(APITestCase):
    def setUp(self):
        self.url = reverse('profile')
        self.email = 'profile@example.com'
        self.password = 'password123'
        self.user = User.objects.create_user(
            email=self.email, 
            password=self.password,
            username='profileuser'
        )
        self.profile = UserProfile.objects.create(
            user=self.user, 
            role='EMPLOYER',
            phone='1234567890'
        )
        self.client.force_authenticate(user=self.user)

    def test_get_profile(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['role'], 'EMPLOYER')
        self.assertEqual(response.data['phone'], '1234567890')
        self.assertEqual(response.data['user']['email'], self.email)

    # def test_update_profile(self):
    #     data = {'phone': '0987654321'}
    #     response = self.client.patch(self.url, data)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.profile.refresh_from_db()
    #     self.assertEqual(self.profile.phone, '0987654321')

    def test_unauthenticated_access(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
