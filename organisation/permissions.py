from rest_framework import permissions
from .models import Organisation


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
            # if request.user.is_superuser:
            #     if view.action == 'create' and int(request.data.get("org_fk", 0)) in request.user.organisation_set.values_list('id', flat=True):
            #         return False
            return True
        return False
