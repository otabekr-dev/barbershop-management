from rest_framework.viewsets import ModelViewSet
from .models import Service
from .serializers import ServiceSerializer
from core.permissions import IsAdminOrReadOnly
from django.contrib.auth import get_user_model

User = get_user_model()

class ServiceViewSet(ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Service.objects.none()

        if self.request.user.is_authenticated and self.request.user.role == User.Roles.ADMIN:
            return Service.objects.all()

        return Service.objects.filter(is_active=True)


    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()