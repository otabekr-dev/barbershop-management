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
    telegram_id = models.PositiveBigIntegerField(null=True, blank=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f'{self.id}.{self.phone_number}'