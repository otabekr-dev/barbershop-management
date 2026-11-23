from datetime import datetime, timedelta
from django.utils import timezone
from apps.barbers.models import BarberService, WorkSchedule, TimeOff, Barber
from .models import Booking
from decouple import config
from django.db import transaction, IntegrityError
from rest_framework.exceptions import ValidationError


STEP_MINUTES = config('STEP_MINUTES', cast=int)

def get_available_slots(barber, service, date):

    if not barber.is_active or not service.is_active:
        return []

    if date != timezone.localdate():
        return []

    if not BarberService.objects.filter(barber=barber, service=service).exists():
        return []

    if TimeOff.objects.filter(barber=barber, start_date__lte=date, end_date__gte=date).exists():
        return []

    schedule = WorkSchedule.objects.filter(barber=barber, weekday=date.weekday()).first()

    if not schedule:
        return []

    
    day_start = timezone.make_aware(datetime.combine(date, schedule.start_time))
    day_end = timezone.make_aware(datetime.combine(date, schedule.end_time))

    break_start = None
    break_end = None

    if schedule.break_start is not None:
        break_start = timezone.make_aware(datetime.combine(date, schedule.break_start))
        break_end = timezone.make_aware(datetime.combine(date, schedule.break_end))

    duration = service.duration

    bookings = Booking.objects.filter(
        barber=barber, start_at__lte=day_end, end_at__gte=day_start
    ).exclude(status=Booking.StatusChoice.CANCELLED)

    busy = []

    for booking in bookings:
        busy.append((booking.start_at, booking.end_at))

    result = []
    now = timezone.now()
    current = day_start

    while current + duration <= day_end:
        slot_end = current + duration
        is_free = True

        if current <= now:
            is_free = False

        if is_free and break_start is not None:
            if current < break_end and slot_end > break_start:
                is_free = False

        if is_free:
            for busy_start, busy_end in busy:
                if current < busy_end and slot_end > busy_start:
                    is_free = False
                    break

        if is_free:
            result.append(current)

        current += timedelta(minutes=STEP_MINUTES)

    return result 

def create_booking(barber, service, start_at, customer=None, guest_name='', guest_phone='', note=''):

    try:
        with transaction.atomic():
            barber = Barber.objects.select_for_update().get(pk=barber.pk)
            date = timezone.localtime(start_at).date()
            slots = get_available_slots(barber=barber, service=service, date=date)

            if start_at not in slots:
                raise ValidationError('Bu vaqt band yoki mavjudmas')

            barber_service = BarberService.objects.filter(barber=barber, service=service).first()

            if barber_service.custom_price is not None:
                price = barber_service.custom_price
            else:
                price = service.price

            end_at  = start_at + service.duration

            booking = Booking.objects.create(
                customer=customer,
                barber=barber,
                service=service,
                price=price,
                start_at=start_at,
                end_at=end_at,
                guest_name=guest_name,
                guest_phone=guest_phone,
                note=note,
                status=Booking.StatusChoice.PENDING
            )
    except IntegrityError:
        raise ValidationError('Bu vaqt band bo\'lib qoldi, boshqa vaqt tanlang')
    
    return booking