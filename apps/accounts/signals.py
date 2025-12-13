from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.accounts.models import (
    UserProfile,
    EmployerProfile,
    EmployeeProfile,
    ProviderProfile,
    HMOProfile
)
from apps.enrollees.models import Enrollees

@receiver(post_save, sender=UserProfile)
def create_related_profile(sender, instance, created, **kwargs):
    """
    Automatically create the specific role profile when a UserProfile is created.
    Also implements the 'Claim' logic for Employees.
    """
    if created:
        if instance.role == 'EMPLOYER':
            EmployerProfile.objects.create(
                user_profile=instance,
                company_name=f"Company for {instance.user.email}", # Placeholder
                company_phone=instance.phone or "",
                company_email=instance.user.email
            )
        
        elif instance.role == 'EMPLOYEE':
            # Hybrid/Claim Logic: Check if this user exists as an Enrollee
            employee_profile = EmployeeProfile.objects.create(
                user_profile=instance
            )
            
            # Try to link to an existing Enrollee record by email
            # We use filter().first() to avoid errors if duplicates exist (though email should be unique)
            enrollee = Enrollees.objects.filter(email=instance.user.email).first()
            
            if enrollee:
                # Link the profile to the employer and enrollee details
                employee_profile.employer = enrollee.employer
                employee_profile.employee_id = enrollee.enrollee_id
                employee_profile.job_title = "Employee" # Default
                employee_profile.save()
                
                # Optional: Update the Enrollee record to link back to the user?
                # For now, the link is established via the EmployeeProfile.
        
        elif instance.role == 'PROVIDER':
            ProviderProfile.objects.create(
                user_profile=instance,
                facility_name=f"Facility for {instance.user.email}", # Placeholder
                facility_type='HOSPITAL' # Default, user must update
            )
            
        elif instance.role == 'HMO':
            HMOProfile.objects.create(
                user_profile=instance,
                hmo_name=f"HMO for {instance.user.email}",
                contact_email=instance.user.email,
                contact_phone=instance.phone or ""
            )

@receiver(post_save, sender=UserProfile)
def save_related_profile(sender, instance, **kwargs):
    """
    Ensure the related profile is saved when the UserProfile is saved.
    """
    if instance.role == 'EMPLOYER' and hasattr(instance, 'employer_profile'):
        instance.employer_profile.save()
    elif instance.role == 'EMPLOYEE' and hasattr(instance, 'employee_profile'):
        instance.employee_profile.save()
    elif instance.role == 'PROVIDER' and hasattr(instance, 'provider_profile'):
        instance.provider_profile.save()
    elif instance.role == 'HMO' and hasattr(instance, 'hmo_profile'):
        instance.hmo_profile.save()



