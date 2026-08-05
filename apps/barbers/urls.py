from django.urls import path
from .views import BarberView, BarberDetailView, BarberAvailabilityView, BarberAssignServiceView

urlpatterns = [
    path('', BarberView.as_view(), name='barber'),
    path('<int:pk>/', BarberDetailView.as_view(), name='barber-detail'),
    path('<int:pk>/availability/', BarberAvailabilityView.as_view(), name='barber-availability'),
    path('<int:pk>/assign-services/', BarberAssignServiceView.as_view(), name='barber-assign-service')
]
