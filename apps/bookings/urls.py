from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import BookingViewSet, AvailableSlotsView

router = DefaultRouter()
router.register('bookings', BookingViewSet, basename='booking')

urlpatterns = [
    path('barbers/<int:pk>/available-slots/', AvailableSlotsView.as_view()),
] + router.urls