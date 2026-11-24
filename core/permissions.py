import secrets
from rest_framework.permissions import BasePermission, SAFE_METHODS
from django.contrib.auth import get_user_model
from decouple import config

TELEGRAM_BOT_SECRET=config('TELEGRAM_BOT_SECRET')

User = get_user_model()

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.Roles.ADMIN

class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.Roles.MANAGER

class IsBarber(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.Roles.BARBER

class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.Roles.CUSTOMER

class IsAdminOrManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [User.Roles.ADMIN, User.Roles.MANAGER]

class IsBranchManagerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.role == User.Roles.ADMIN:
            return True
        if request.method in SAFE_METHODS:
            return True

        return obj.manager == request.user

class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.role == User.Roles.ADMIN:
            return True
        
        return request.method in SAFE_METHODS

class IsAdminOrManagerOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if request.user.is_authenticated and request.user.role in [User.Roles.ADMIN, User.Roles.MANAGER]:
            return True

        return request.method in SAFE_METHODS

class IsTelegramBot(BasePermission):

    def has_permission(self, request, view):
        provided_secret = request.headers.get('X-BOT-SECRET', '')

        return secrets.compare_digest(
            provided_secret,
            TELEGRAM_BOT_SECRET
        )