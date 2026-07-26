from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsBarberOrAdmin(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        if request.user.is_authenticated and request.user.role in ['BARBER', 'ADMIN']:
            return True
        
        return False