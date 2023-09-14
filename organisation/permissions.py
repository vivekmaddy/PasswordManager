from rest_framework import permissions
from .models import SharedPasswords, Passwords


class IsSuperUser(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.is_superuser:
            return True
        return False

class IsOrgSuperUser(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.is_superuser and int(request.data.get("org_fk")) in request.user.organisation_set.values_list('id', flat=True):
            return True
        return False

class PasswordPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True
        return False
    
    def has_object_permission(self, request, view, obj):
        shared = SharedPasswords.objects.filter(password=obj, shared_to=request.user).first()
        if request.user.is_superuser and request.method in ['POST']:
            return True
        elif shared and request.method in ['PUT', 'PATCH'] and shared.edit == True and shared.shared_to == request.user:
            return True
        elif shared and request.method == 'GET' and shared.view == True and shared.shared_to == request.user:
            return True
        return False


