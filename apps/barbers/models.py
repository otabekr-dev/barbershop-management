from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import CheckConstraint, F, Q, UniqueConstraint

from apps.branch.models import Branch
from apps.service.models import Service


class Barber(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='barber_profile',
        limit_choices_to={'role': 'BARBER'},
    )
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name='barbers')
    bio = models.TextField(default='', blank=True)
    experience_years = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f'{self.pk}.{self.user.first_name}'


class BarberService(models.Model):
    barber = models.ForeignKey(Barber, on_delete=models.CASCADE, related_name='barber_services')
    service = models.ForeignKey(Service, on_delete=models.PROTECT, related_name='barber_services')
    custom_price = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']
        constraints = [
            UniqueConstraint(fields=['barber', 'service'], name='barber_service_unique'),
        ]

    def __str__(self):
        return f'{self.barber} - {self.service}'


class WorkSchedule(models.Model):
    class Weekday(models.IntegerChoices):
        MONDAY = 0, "Dushanba"
        TUESDAY = 1, "Seshanba"
        WEDNESDAY = 2, "Chorshanba"
        THURSDAY = 3, "Payshanba"
        FRIDAY = 4, "Juma"
        SATURDAY = 5, "Shanba"
        SUNDAY = 6, "Yakshanba"

    barber = models.ForeignKey(Barber, on_delete=models.CASCADE, related_name='schedules')
    weekday = models.IntegerField(choices=Weekday.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()
    break_start = models.TimeField(null=True, blank=True)
    break_end = models.TimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['barber', 'weekday']
        constraints = [
            UniqueConstraint(
                fields=['barber', 'weekday'],
                name='workschedule_unique_barber_weekday',
            ),
            CheckConstraint(
                condition=Q(end_time__gt=F('start_time')),
                name='workschedule_end_after_start',
            ),
        ]

    def clean(self):
        
        if self.start_time is None or self.end_time is None:
            return

        if (self.break_start is None) != (self.break_end is None):
            raise ValidationError('Tanaffusning boshlanishi va tugashi birga kiritilishi shart')

        if self.break_start is not None:
            if self.break_end <= self.break_start:
                raise ValidationError("Tanaffus tugashi boshlanishidan keyin bo'lishi kerak")

            if self.break_start < self.start_time or self.break_end > self.end_time:
                raise ValidationError("Tanaffus ish vaqtining ichida bo'lishi shart")

    def __str__(self):
        return f'{self.pk}.{self.barber} - {self.get_weekday_display()}'


class TimeOff(models.Model):
    barber = models.ForeignKey(Barber, on_delete=models.CASCADE, related_name='time_offs')
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']
        constraints = [
            CheckConstraint(
                condition=Q(end_date__gte=F('start_date')),
                name='timeoff_end_not_before_start',
            ),
        ]

    def clean(self):
        if self.start_date is not None and self.end_date is not None:
            if self.end_date < self.start_date:
                raise ValidationError("Tugash sanasi boshlanish sanasidan oldin bo'la olmaydi")

    def __str__(self):
        return f'{self.barber}: {self.start_date} - {self.end_date}'