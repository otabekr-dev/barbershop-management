from django.urls import path
from .views import BookingListCreateView, BookingDetailView, BookingStatusUpdateView


urlpatterns = [
    path('', BookingListCreateView.as_view()),
    path('<int:pk>/', BookingDetailView.as_view()),
    path('<int:pk>/status/', BookingStatusUpdateView.as_view())
]
