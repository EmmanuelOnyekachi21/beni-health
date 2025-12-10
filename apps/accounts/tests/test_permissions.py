from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from apps.accounts.models import UserProfile
from apps.accounts.permissions import (
    IsEmployer, IsEmployee, IsProvider, IsHMO, IsAdmin
)

User = get_user_model()

class PermissionsTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        
        # Create users with different roles
        self.employer_user = User.objects.create_user(email='employer@test.com', password='pw', username='emp')
        UserProfile.objects.create(user=self.employer_user, role='EMPLOYER')
        
        self.employee_user = User.objects.create_user(email='employee@test.com', password='pw', username='worker')
        UserProfile.objects.create(user=self.employee_user, role='EMPLOYEE')
        
        self.provider_user = User.objects.create_user(email='provider@test.com', password='pw', username='doc')
        UserProfile.objects.create(user=self.provider_user, role='PROVIDER')
        
        self.hmo_user = User.objects.create_user(email='hmo@test.com', password='pw', username='insurer')
        UserProfile.objects.create(user=self.hmo_user, role='HMO')
        
        self.admin_user = User.objects.create_user(email='admin@test.com', password='pw', username='boss')
        UserProfile.objects.create(user=self.admin_user, role='ADMIN')

    def _check_permission(self, user, permission_class):
        request = self.factory.get('/')
        request.user = user
        permission = permission_class()
        return permission.has_permission(request, None)

    def test_is_employer_permission(self):
        self.assertTrue(self._check_permission(self.employer_user, IsEmployer))
        self.assertFalse(self._check_permission(self.employee_user, IsEmployer))
        self.assertFalse(self._check_permission(self.provider_user, IsEmployer))

    def test_is_employee_permission(self):
        self.assertTrue(self._check_permission(self.employee_user, IsEmployee))
        self.assertFalse(self._check_permission(self.employer_user, IsEmployee))

    def test_is_provider_permission(self):
        self.assertTrue(self._check_permission(self.provider_user, IsProvider))
        self.assertFalse(self._check_permission(self.employer_user, IsProvider))

    def test_is_hmo_permission(self):
        self.assertTrue(self._check_permission(self.hmo_user, IsHMO))
        self.assertFalse(self._check_permission(self.employer_user, IsHMO))

    def test_is_admin_permission(self):
        self.assertTrue(self._check_permission(self.admin_user, IsAdmin))
        self.assertFalse(self._check_permission(self.employer_user, IsAdmin))
