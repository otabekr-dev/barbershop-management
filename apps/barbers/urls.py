from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import BarberViewSet, BarberRegisterView, WorkScheduleViewSet, TimeOffViewSet, BarberServiceViewSet

routers = DefaultRouter()
routers.register('barber', BarberViewSet, basename='barber_viewset')
routers.register('work-schedule', WorkScheduleViewSet, basename='work_schedule_viewset')
routers.register('time-off', TimeOffViewSet, basename='time_off_viewset')
routers.register('barber-service', BarberServiceViewSet, basename='barber_service_viewset')

urlpatterns = [
    path('barber-register/', BarberRegisterView.as_view(), name='barber-register')
] + routers.urls