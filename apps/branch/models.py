from django.db import models
from django.conf import settings
from core.validators import validate_uzb_numbers

class Branch(models.Model):
    name = models.CharField(max_length=150)
    address = models.TextField()
    phone_number = models.CharField(max_length=13, validators=[validate_uzb_numbers])
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, 
        on_delete=models.SET_NULL,
        related_name='managed_branches',
        limit_choices_to={'role':'MANAGER'}    
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.id}.{self.name}'