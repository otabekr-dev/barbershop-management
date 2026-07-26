from django.urls import path
from .views import ServiceView, ServiceDetailView

urlpatterns = [
    path('services/', ServiceView.as_view(), name='services'),
    path('services/<int:pk>/', ServiceDetailView.as_view(), name='service-details')
]
