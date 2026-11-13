from .views import MeView, RegisterView
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/me/', MeView.as_view(), name='me-view'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]