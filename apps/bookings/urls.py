from django.urls import path
from .views import BookingListCreateView, BookingDetailView, BookingStatusUpdateView, AvailableSlotsView


urlpatterns = [
    path('', BookingListCreateView.as_view()),
    path('<int:pk>/', BookingDetailView.as_view()),
    path('<int:pk>/status/', BookingStatusUpdateView.as_view()),
    path('<int:pk>/available-slots/', AvailableSlotsView.as_view())
]
