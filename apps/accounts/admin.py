from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import (
    User,
    UserProfile,
    EmployerProfile,
    EmployeeProfile,
    ProviderProfile,
    HMOProfile,
)


# ------------------------
# Custom User Admin
# ------------------------
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom admin panel for the User model."""

    ordering = ('email',)
    list_display = ('email', 'first_name', 'last_name', 'username', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_active', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name')

    # Use email as username
    fieldsets = (
        (None, {'fields': ('id', 'email', 'password')}),
        (_('Personal Info'), {'fields': ('first_name', 'last_name', 'username')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important Dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'username', 'password1', 'password2'),
        }),
    )

    readonly_fields = ('id', 'date_joined', 'last_login')


# ------------------------
# User Profile Admin
# ------------------------
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone', 'created_at')
    search_fields = ('user__email', 'phone', 'role')
    list_filter = ('role',)
    readonly_fields = ('id', 'created_at', 'updated_at')


# ------------------------
# Employer Profile Admin
# ------------------------
@admin.register(EmployerProfile)
class EmployerProfileAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'user_profile', 'company_phone', 'company_email')
    search_fields = ('company_name', 'company_registration_number', 'company_email')
    readonly_fields = ('id', 'created_at', 'updated_at')


# ------------------------
# Employee Profile Admin
# ------------------------
@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = ('get_user', 'employer', 'employee_id', 'department', 'job_title')
    search_fields = ('employee_id', 'user_profile__user__email', 'department', 'job_title')
    list_filter = ('department',)
    readonly_fields = ('id', 'created_at', 'updated_at')

    def get_user(self, obj):
        return obj.user_profile.user.get_full_name()
    get_user.short_description = "Employee Name"


# ------------------------
# Provider Profile Admin
# ------------------------
@admin.register(ProviderProfile)
class ProviderProfileAdmin(admin.ModelAdmin):
    list_display = ('facility_name', 'facility_type', 'accreditation_status', 'created_at')
    search_fields = ('facility_name', 'license_number')
    list_filter = ('facility_type', 'accreditation_status')
    readonly_fields = ('id', 'created_at', 'updated_at')


# ------------------------
# HMO Profile Admin
# ------------------------
@admin.register(HMOProfile)
class HMOProfileAdmin(admin.ModelAdmin):
    list_display = ('hmo_name', 'contact_email', 'contact_phone')
    search_fields = ('hmo_name', 'contact_email', 'contact_phone')
    readonly_fields = ('id', 'created_at', 'updated_at')
