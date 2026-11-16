from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import BarberViewSet, BarberRegisterView, WorkScheduleViewSet, TimeOffViewSet

routers = DefaultRouter()
routers.register('barber', BarberViewSet, basename='barber_viewset')
routers.register('work_schedule', WorkScheduleViewSet, basename='work_schedule_viewset')
routers.register('time_off', TimeOffViewSet, basename='time_off_viewset')

urlpatterns = [
    path('barber-register/', BarberRegisterView.as_view(), name='barber-register')
] + routers.urls