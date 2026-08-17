from django.urls import path
from .views import BookingListCreateView, BookingDetailView, BookingStatusUpdateView, AvailableSlotsView, CancelAppointmentView


urlpatterns = [
    path('', BookingListCreateView.as_view(), name='booking'),
    path('<int:pk>/', BookingDetailView.as_view(), name='booking-details'),
    path('<int:pk>/status/', BookingStatusUpdateView.as_view(), name='booking-status-update'),
    path('<int:pk>/available-slots/', AvailableSlotsView.as_view(), name='available-slots'),
    path('<int:pk>/cancel/', CancelAppointmentView.as_view(), name='cancel')
]
