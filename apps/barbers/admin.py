from django.contrib import admin
from .models import BarberService,Barber,TimeOff,WorkSchedule
admin.site.register([Barber, BarberService, TimeOff, WorkSchedule])