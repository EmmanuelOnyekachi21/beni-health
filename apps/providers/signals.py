from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.accounts.models import UserProfile
from apps.providers.models import ProviderProfile

@receiver(post_save, sender=UserProfile)
def create_provider_profile(sender, instance, created, **kwargs):
    """
    When a user registers as PROVIDER, create a basic Provider record.
    They'll need to complete it with facility details later.
    """
    if created and instance.role == 'PROVIDER':
        ProviderProfile.objects.create(
            user_profile=instance,
            facility_name=f"Facility - {instance.user.email}",  # Placeholder
            facility_type='HOSPITAL',  # Default
            contact_phone=instance.phone or '',
            contact_email=instance.user.email,
            accreditation_status='PENDING'
        )