from rest_framework.permissions import BasePermission

class IsEmployer(BasePermission):
    """
    Permission class to check if the user is an employer
    """
    def has_permission(self, request, view):
        return (
            request.user and request.user.is_authenticated
            and hasattr(request.user, 'profile')
            and request.user.profile.role == 'EMPLOYER'
        )


class IsEmployee(BasePermission):
    """
    Permission class to check if the user is an employee
    """
    def has_permission(self, request, view):
        return (
            request.user and request.user.is_authenticated
            and hasattr(request.user, 'profile')
            and request.user.profile.role == 'EMPLOYEE'
        )

class IsProvider(BasePermission):
    """
    Permission class to check if the user is a provider.
    """
    def has_permission(self, request, view):
        return (
            request.user and request.user.is_authenticated
            and hasattr(request.user, 'profile')
            and request.user.profile.role == 'PROVIDER'
        )

class IsAdmin(BasePermission):
    """
    Permission class to check if the user is an admin.
    """
    def has_permission(self, request, view):
        return (
            request.user and request.user.is_authenticated
            and hasattr(request.user, 'profile')
            and request.user.profile.role == 'ADMIN'
        )



class IsHMO(BasePermission):
    """
    Permission class to check if the user is an HMO.
    """
    def has_permission(self, request, view):
        return (
            request.user and request.user.is_authenticated
            and hasattr(request.user, 'profile')
            and request.user.profile.role == 'HMO')

