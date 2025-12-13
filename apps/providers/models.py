import uuid
from django.db import models
from apps.accounts.models import UserProfile
from datetime import time
from django.utils import timezone


class ProviderProfile(models.Model):
    """
    Represents a healthcare organization (legal entity).
    Example: 'MediCare Health Services Ltd'
    """

    # ============================
    # Facility type choices
    # ============================
    FACILITY_TYPE_CHOICES = (
        ('HOSPITAL', 'Hospital'),
        ('CLINIC', 'Clinic'),
        ('DIAGNOSTIC', 'Diagnostic Center'),
        ('PHARMACY', 'Pharmacy'),
        ('SPECIALIST', 'Specialist Center'),
        ('DENTAL', 'Dental Clinic'),
        ('EYE', 'Eye Clinic'),
    )

    # ============================
    # Accreditation status choices
    # ============================
    ACCREDITATION_STATUS_CHOICES = (
        ('PENDING', 'Pending Review'),
        ('VERIFIED', 'Verified'),
        ('ACTIVE', 'Active'),
        ('SUSPENDED', 'Suspended'),
        ('REJECTED', 'Rejected'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user_profile = models.OneToOneField(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='provider'
    )

    facility_name = models.CharField(max_length=200)

    facility_type = models.CharField(
        max_length=50,
        choices=FACILITY_TYPE_CHOICES
    )

    license_number = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    accreditation_status = models.CharField(
        max_length=20,
        choices=ACCREDITATION_STATUS_CHOICES,
        default='PENDING'
    )

    contact_phone = models.CharField(max_length=20)
    contact_email = models.EmailField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'providers'
        ordering = ['facility_name']
        indexes = [
            models.Index(fields=['facility_type']),
            models.Index(fields=['accreditation_status']),
        ]

    def __str__(self):
        return self.facility_name

    def is_operational(self):
        """
        Provider-level eligibility (contracts & trust).
        """
        return (
            self.accreditation_status == 'ACTIVE'
            and self.user_profile.user.is_active
        )


class ProviderLocation(models.Model):
    """
    Represents a location of a provider.
    Example: 'MediCare Health Services Ltd - Main Hospital'
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provider = models.ForeignKey(ProviderProfile, on_delete=models.CASCADE, related_name='locations')
    branch_name = models.CharField(max_length=200)
    address = models.JSONField(default=dict)

    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )

    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )

    contact_phone = models.CharField(max_length=20)

    # ============================
    # Services (branch-specific)
    # ============================
    services = models.ManyToManyField(
        'Service',
        blank=True,
        related_name='provider_locations'
    )

    # ============================
    # Operating hours
    # ============================
    operating_hours = models.JSONField(
        null=True,
        blank=True,
        help_text='{"monday": {"open": "08:00", "close": "17:00"}}'
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'provider_locations'
        indexes = [
            models.Index(fields=['latitude', 'longitude']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.provider.facility_name} - {self.branch_name}"

    # ==================================
    # Location-level operational checks
    # ==================================
    def is_operational(self):
        """
        Location is operational only if:
        - Provider is operational
        - Location is active
        """
        return self.is_active and self.provider.is_operational()
    
    def is_open_now(self):
        """
        Check if the location is open now based on operating hours.
        """
        if not self.operating_hours:
            return True
        
        now = timezone.localtime()
        day_name = now.strftime('%A').lower()

        today = self.operating_hours.get(day_name)
        if not today:
            return False
        
        try:
            open_time = time.fromisoformat(today['open'])
            close_time = time.fromisoformat(today['close'])
        except (KeyError, ValueError):
            return False
        
        return open_time <= now.time() <= close_time
    

class Service(models.Model):
    """
    Standardized medical service catalog.
    """
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=100)  # Lab, Radiology, Surgery
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.code})"



