from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsBookingOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if obj.customer == request.user:
            return True

        return False