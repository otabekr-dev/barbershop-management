from .views import MeView, RegisterView, StaffCreateView
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('manager/', StaffCreateView.as_view(), name='staff-create'),
    path('auth/login/', TokenObtainPairView.as_view(), name='login'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/me/', MeView.as_view(), name='me-view'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]