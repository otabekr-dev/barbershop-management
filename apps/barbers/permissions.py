from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerBarberOrAdmin(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        if request.user.is_authenticated and request.user.role in ['BARBER', 'ADMIN']:
            return True

        return False

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if request.user.role == 'ADMIN':
            return True
        if obj.user == request.user:
            return True

        return False


class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "ADMIN"
 