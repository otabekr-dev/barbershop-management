from django.db import models
from django.core.validators import MinValueValidator
from django.db.models import CheckConstraint, Q, UniqueConstraint
from datetime import timedelta
from core.validators import validate_service_duration
from django.db.models.functions import Lower

class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(default='', blank=True)
    price = models.DecimalField(
        max_digits=10, decimal_places=0,
        validators=[MinValueValidator(1)]
    )
    duration = models.DurationField(
        validators=[validate_service_duration]
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']
        constraints = [
            CheckConstraint(
                condition=Q(price__gt=0),
                name='service_price_positive'
            ),
            CheckConstraint(
                condition=Q(duration__gt=timedelta(0)),
                name='service_duration_positive'
            ),
            UniqueConstraint(
                Lower('name'),
                name='service_name_unique_ci'
            ),
        ]

    def __str__(self):
        return f'{self.id}.{self.name}'