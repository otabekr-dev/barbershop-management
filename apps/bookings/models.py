from django.conf import settings
from django.contrib.postgres.constraints import ExclusionConstraint
from django.contrib.postgres.fields import (
    DateTimeRangeField,
    RangeBoundary,
    RangeOperators,
)
from django.db import models
from django.db.models import F, Func, Q

from apps.barbers.models import Barber
from apps.service.models import Service
from core.validators import validate_uzb_numbers


class TsTzRange(Func):
    function = 'TSTZRANGE'
    output_field = DateTimeRangeField()


class Booking(models.Model):
    class StatusChoice(models.TextChoices):
        PENDING = 'PENDING', 'Kutilmoqda'
        CONFIRMED = 'CONFIRMED', 'Tasdiqlandi'
        COMPLETED = 'COMPLETED', 'Bajarildi'
        CANCELLED = 'CANCELLED', 'Bekor qilindi'
        NO_SHOW = 'NO_SHOW', 'Kelmadi'

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='bookings',
    )


    guest_name = models.CharField(max_length=150, blank=True, default='')
    guest_phone = models.CharField(
        max_length=13,
        blank=True,
        default='',
        validators=[validate_uzb_numbers],
    )

    barber = models.ForeignKey(
        Barber,
        on_delete=models.PROTECT,
        related_name='bookings',
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.PROTECT,
        related_name='bookings',
    )

    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    price = models.DecimalField(max_digits=10, decimal_places=0)

    status = models.CharField(
        max_length=20,
        choices=StatusChoice.choices,
        default=StatusChoice.PENDING,
    )
    note = models.TextField(blank=True, default='')

    cancelled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cancelled_bookings',
    )
    cancelled_reason = models.TextField(blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_at']
        indexes = [
            models.Index(fields=['barber', 'start_at']),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(end_at__gt=F('start_at')),
                name='booking_end_after_start',
            ),
            models.CheckConstraint(
                condition=Q(price__gt=0),
                name='booking_price_positive',
            ),
            models.CheckConstraint(
                condition=Q(customer__isnull=False) | ~Q(guest_phone=''),
                name='booking_customer_or_guest',
            ),
            ExclusionConstraint(
                name='booking_no_overlap_per_barber',
                expressions=[
                    (TsTzRange('start_at', 'end_at', RangeBoundary()), RangeOperators.OVERLAPS),
                    ('barber', RangeOperators.EQUAL),
                ],
                
                condition=~Q(status='CANCELLED'),
            ),
        ]

    def __str__(self):
        return f'{self.pk}.{self.barber} - {self.start_at:%Y-%m-%d %H:%M}'