from django.db import models
from django.conf import settings
from apps.services.models import Service


class Barber(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    services = models.ManyToManyField(Service, related_name='barbers')
    is_available = models.BooleanField(default=True)


    def __str__(self):
        return f'{self.id}.{self.user.username}'