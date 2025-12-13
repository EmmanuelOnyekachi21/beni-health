from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from apps.enrollees.models import Enrollees
from django.utils import timezone
from apps.accounts.models import User, EmployeeProfile


def generate_enrollee_id():
    """
    Generate unique enrollee ID in format: HL-YYMMDD-XXXX.
    Example: HL-241210-0001
    """
    today = timezone.now()
    date_part = today.strftime('%y%m%d')  # YYMMDD format

    # Get count of enrollees created today
    count_today = Enrollees.objects.filter(
        created_at__date=today.date()
    ).count()

    # Next Sequence number
    sequence_number = str(count_today + 1).zfill(4)
    return f"HL-{date_part}-{sequence_number}"


@receiver(pre_save, sender=Enrollees)
def auto_generate_enrollee_id(sender, instance, **kwargs):
    """
    Automatically generate enrollee ID if not provided before saving if not provided.
    """
    if not instance.enrollee_id:
        instance.enrollee_id = generate_enrollee_id()

@receiver(post_save, sender=Enrollees)
def link_enrollee_to_user(sender, instance, created, **kwargs):
    """
    When an Enrollee is created, check if a User account exists
    with matching email. If yes, create or update the EmployeeProfile.
    
    This handles the scenario where:
    - Day 1: Employee self-registers (EmployeeProfile created, not linked)
    - Day 5: Employer enrolls employee (this signal links them)
    """
    if created and instance.email:  # Only process if email is provided
        try:
            user = User.objects.get(email=instance.email)

            # Check if the user has a profile
            if not hasattr(user, 'profile') or user.profile is None:
                # User exists but no UserProfile yet - skip linking
                # This shouldn't happen in normal flow, but we handle it gracefully
                return

            # Only proceed if the user is an Employee
            if user.profile.role != 'EMPLOYEE':
                return

            # Get or create the EmployeeProfile
            employee_profile, profile_created = EmployeeProfile.objects.get_or_create(
                user_profile=user.profile,
                defaults={
                    'employer': instance.employer,
                    'employee_id': instance.enrollee_id,
                    'date_of_birth': instance.dob,
                }
            )

            # If profile already existed but wasn't linked, update it
            if not profile_created and not employee_profile.employer:
                employee_profile.employer = instance.employer
                employee_profile.employee_id = instance.enrollee_id
                employee_profile.date_of_birth = instance.dob
                employee_profile.save()
                
        except User.DoesNotExist:
            # No user with this email - this is fine, they can claim later
            # When they register, the accounts/signals.py will link them
            pass


