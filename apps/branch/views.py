from rest_framework.viewsets import ModelViewSet
from .models import Branch
from .serializers import BranchSerializer
from core.permissions import IsAdmin, IsBranchManagerOrAdmin
from rest_framework.response import Response
from django.contrib.auth import get_user_model


User = get_user_model()

class BranchViewSet(ModelViewSet):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer

    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            return [IsAdmin()]
        return [IsBranchManagerOrAdmin()]

    def get_queryset(self):

        if getattr(self, 'swagger_fake_view', False):
            return Branch.objects.none()

        if self.request.user.role == User.Roles.ADMIN:
            return Branch.objects.all()
        elif self.request.user.role == User.Roles.MANAGER:
            return Branch.objects.filter(manager=self.request.user)

        return Branch.objects.filter(is_active=True)

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()