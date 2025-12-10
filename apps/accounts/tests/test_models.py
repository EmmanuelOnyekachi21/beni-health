from django.test import TestCase
from django.db.utils import IntegrityError
from apps.accounts.models import (
    User, UserProfile, EmployerProfile, EmployeeProfile, 
    ProviderProfile, HMOProfile
)

class UserModelTest(TestCase):
    def test_create_user(self):
        """Test creating a standard user with email as username."""
        user = User.objects.create_user(
            email='test@example.com',
            password='password123',
            first_name='Test',
            last_name='User',
            username='testuser'
        )
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('password123'))
        self.assertEqual(str(user), 'test@example.com')

    def test_create_superuser(self):
        """Test creating a superuser."""
        admin = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass',
            first_name='Admin',
            last_name='User',
            username='adminuser'
        )
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)

    def test_email_unique(self):
        """Test that email must be unique."""
        User.objects.create_user(email='unique@example.com', password='pw', username='uniqueuser')
        with self.assertRaises(IntegrityError):
            User.objects.create_user(email='unique@example.com', password='pw2', username='uniqueuser2')


class UserProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='profile@example.com', password='pw', username='profileuser')

    def test_create_user_profile(self):
        profile = UserProfile.objects.create(
            user=self.user,
            role='EMPLOYER',
            phone='1234567890'
        )
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.role, 'EMPLOYER')
        self.assertIn('Employer', str(profile))


class EmployerProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='employer@example.com', password='pw', username='employeruser')
        self.profile = UserProfile.objects.create(user=self.user, role='EMPLOYER')

    def test_create_employer_profile(self):
        employer = EmployerProfile.objects.create(
            user_profile=self.profile,
            company_name='Tech Corp',
            company_phone='0987654321',
            company_email='contact@techcorp.com'
        )
        self.assertEqual(employer.company_name, 'Tech Corp')
        self.assertEqual(employer.user_profile, self.profile)
        self.assertIn('Tech Corp', str(employer))


class EmployeeProfileModelTest(TestCase):
    def setUp(self):
        # Create Employer
        emp_user = User.objects.create_user(email='boss@example.com', password='pw', username='bossuser')
        emp_profile = UserProfile.objects.create(user=emp_user, role='EMPLOYER')
        self.employer = EmployerProfile.objects.create(
            user_profile=emp_profile,
            company_name='Big Corp',
            company_phone='111',
            company_email='big@corp.com'
        )
        
        # Create Employee User
        self.user = User.objects.create_user(email='worker@example.com', password='pw', username='workeruser')
        self.profile = UserProfile.objects.create(user=self.user, role='EMPLOYEE')

    def test_create_employee_profile(self):
        employee = EmployeeProfile.objects.create(
            user_profile=self.profile,
            employer=self.employer,
            employee_id='EMP001',
            job_title='Developer'
        )
        self.assertEqual(employee.employer, self.employer)
        self.assertEqual(employee.employee_id, 'EMP001')


class ProviderProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='doc@example.com', password='pw', username='docuser')
        self.profile = UserProfile.objects.create(user=self.user, role='PROVIDER')

    def test_create_provider_profile(self):
        provider = ProviderProfile.objects.create(
            user_profile=self.profile,
            facility_name='City Hospital',
            facility_type='HOSPITAL'
        )
        self.assertEqual(provider.facility_name, 'City Hospital')
        self.assertEqual(provider.facility_type, 'HOSPITAL')


class HMOProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='hmo@example.com', password='pw', username='hmouser')
        self.profile = UserProfile.objects.create(user=self.user, role='HMO')

    def test_create_hmo_profile(self):
        hmo = HMOProfile.objects.create(
            user_profile=self.profile,
            hmo_name='HealthGuard',
            contact_email='support@healthguard.com',
            contact_phone='555-0199'
        )
        self.assertEqual(hmo.hmo_name, 'HealthGuard')
        self.assertEqual(hmo.contact_email, 'support@healthguard.com')
