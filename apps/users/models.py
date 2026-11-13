from django.db import models
from django.contrib.auth.models import AbstractUser
from core.validators import validate_uzb_numbers
from apps.users.managers import CustomUserManager

class CustomUser(AbstractUser):
    class Roles(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        MANAGER = 'MANAGER', 'Manager'
        BARBER = 'BARBER', 'Barber'
        CUSTOMER = 'CUSTOMER', 'Customer'

    phone_number = models.CharField(unique=True,max_length=13,validators=[validate_uzb_numbers])
    username = None
    role = models.CharField(choices=Roles.choices, default=Roles.CUSTOMER, max_length=10)
    email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []