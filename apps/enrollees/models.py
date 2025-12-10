from django.db import models
from apps.accounts.models import EmployerProfile
from apps.plans.models import Plan
import uuid

# Create your models here.
class Enrollees(models.Model):
    """
    An enrollee is an employee or member covered by health insurance.
    This is the central model connecting employees to plans and claims.
    """
    STATUS_CHOICES = (
        ('ACTIVE', 'Active'),
        ('SUSPENDED', 'Suspended'),
        ('TERMINATED', 'Terminated'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    enrollee_id = models.CharField(max_length=50, unique=True, db_index=True)
    
    # Personal Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    dob = models.DateField(verbose_name="Date of Birth")
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female')])
    phone = models.CharField(max_length=20, unique=True)
    email = models.EmailField(null=True, blank=True)
    national_id = models.CharField(max_length=50, null=True, blank=True)
    
    # Address (stored as JSON for flexibility)
    address = models.JSONField(default=dict)  # {street, city, state, country}
    
    # Insurance Information
    employer = models.ForeignKey(
        EmployerProfile,
        on_delete=models.SET_NULL,
        null=True,
        related_name='enrollees'
    )

    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name='enrollees')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    coverage_start = models.DateField()
    coverage_end = models.DateField()
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'enrollees'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['enrollee_id']),
            models.Index(fields=['phone']),
            models.Index(fields=['status', 'coverage_start']),
        ]
    
    def __str__(self):
        return f"{self.enrollee_id} - {self.first_name} {self.last_name}"
    
    def is_coverage_active(self):
        """Check if enrollee's coverage is currently active"""
        from django.utils import timezone
        today = timezone.now().date()
        return (
            self.status == 'ACTIVE' and
            self.coverage_start <= today <= self.coverage_end
        )