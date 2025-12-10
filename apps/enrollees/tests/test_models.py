from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from apps.enrollees.models import Enrollees
from apps.plans.models import Plan
from apps.accounts.models import User, UserProfile, EmployerProfile

class EnrolleesModelTest(TestCase):
    def setUp(self):
        # Create Plan
        self.plan = Plan.objects.create(
            plan_code='PLAN001',
            name='Gold Plan',
            description='Premium coverage',
            annual_cap=1000000.00,
            visit_cap=10,
            covered_services=['consultation', 'drugs'],
            co_pay_rules={'consultation': 1000}
        )
        
        # Create Employer
        self.user = User.objects.create_user(email='employer@test.com', password='pw', username='emp')
        self.profile = UserProfile.objects.create(user=self.user, role='EMPLOYER')
        self.employer = EmployerProfile.objects.create(
            user_profile=self.profile,
            company_name='Test Corp',
            company_phone='123',
            company_email='test@corp.com'
        )

    def test_create_enrollee(self):
        enrollee = Enrollees.objects.create(
            enrollee_id='BENI/001',
            first_name='John',
            last_name='Doe',
            dob='1990-01-01',
            gender='M',
            phone='08012345678',
            email='john@doe.com',
            employer=self.employer,
            plan=self.plan,
            coverage_start=timezone.now().date(),
            coverage_end=timezone.now().date() + timedelta(days=365)
        )
        self.assertEqual(enrollee.first_name, 'John')
        self.assertEqual(enrollee.plan, self.plan)
        self.assertEqual(str(enrollee), 'BENI/001 - John Doe')

    def test_is_coverage_active(self):
        today = timezone.now().date()
        enrollee = Enrollees.objects.create(
            enrollee_id='BENI/002',
            first_name='Jane',
            last_name='Doe',
            dob='1992-01-01',
            gender='F',
            phone='08098765432',
            plan=self.plan,
            coverage_start=today - timedelta(days=30),
            coverage_end=today + timedelta(days=335),
            status='ACTIVE'
        )
        self.assertTrue(enrollee.is_coverage_active())

        # Test expired coverage
        enrollee.coverage_end = today - timedelta(days=1)
        enrollee.save()
        self.assertFalse(enrollee.is_coverage_active())

        # Test suspended status
        enrollee.coverage_end = today + timedelta(days=335)
        enrollee.status = 'SUSPENDED'
        enrollee.save()
        self.assertFalse(enrollee.is_coverage_active())
