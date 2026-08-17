from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsBookingOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if obj.customer == request.user:
            return True

        return False

class IsBookingParticipantOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.customer == request.user:
            return True
        if obj.barber.user == request.user:
            return True
        if request.user.role == "ADMIN":
            return True

        return False

class IsAssignedBarberOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.barber.user == request.user:
            return True
        if request.user.role == "ADMIN":
            return True

        return False