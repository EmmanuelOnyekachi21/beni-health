from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid



class User(AbstractUser):
    """
    Custom user model that extends Django's AbstractUser.
    Uses email as the primary identifier instead of username.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, db_index=True)
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)
    # username = None

    
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"


class UserProfile(models.Model):
    """
    Extended user profile with role and additional information.
    One-to-one relationship with User model.
    """
    USER_ROLES = [
        ('EMPLOYER', 'Employer/HR Admin'),
        ('EMPLOYEE', 'Employee/Member'),
        ('PROVIDER', 'Hospital/Provider'),
        ('HMO', 'HMO/Insurance'),
        ('ADMIN', 'Beni Health Admin'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=USER_ROLES)
    phone = models.CharField(max_length=15, unique=True, db_index=True, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_profiles'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f'{self.user.email} - {self.get_role_display()}'


class EmployerProfile(models.Model):
    """
    Additional information for Employer/HR Admin users.
    One-to-one relationship with UserProfile model.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='employer_profile')
    company_name = models.CharField(max_length=100)
    company_registration_number = models.CharField(max_length=100, null=True, blank=True)
    industry = models.CharField(max_length=100, null=True, blank=True)
    number_of_employees = models.IntegerField(default=0)
    company_address = models.JSONField(default=dict)
    company_phone = models.CharField(max_length=15, unique=True, db_index=True)
    company_email = models.EmailField(unique=True, db_index=True)
    company_logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'employer_profiles'
        verbose_name = 'Employer Profile'
        verbose_name_plural = 'Employer Profiles'
    
    def __str__(self):
        return f"{self.company_name} - {self.user_profile.user.email}"


class EmployeeProfile(models.Model):
    """
    Additional information for Employee/Member users.
    One-to-one relationship with UserProfile model.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='employee_profile')
    employer = models.ForeignKey(EmployerProfile, on_delete=models.SET_NULL, related_name='employees', null=True)
    employee_id = models.CharField(max_length=100, unique=True, db_index=True, null=True, blank=True)
    department = models.CharField(max_length=100, null=True, blank=True)
    job_title = models.CharField(max_length=100, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'employee_profiles'
        verbose_name = 'Employee Profile'
        verbose_name_plural = 'Employee Profiles'
    
    def __str__(self):
        return (
            f"{self.user_profile.user.get_full_name()} - "
            f"{self.employer.company_name if self.employer else 'No Employer'}"
        )

class HMOProfile(models.Model):
    """
    Additional information for HMO users.
    One-to-one relationship with UserProfile model.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='hmo_profile')
    hmo_name = models.CharField(max_length=200)
    hmo_license_number = models.CharField(max_length=100, null=True, blank=True)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'hmo_profiles'
    
    def __str__(self):
        return f"{self.hmo_name}"


