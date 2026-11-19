from rest_framework.generics import CreateAPIView
from rest_framework.viewsets import ModelViewSet
from .models import Barber, BarberService, WorkSchedule, TimeOff
from .serializers import BarberSerializer, BarberRegisterSerializer, WorkScheduleSerializer, TimeOffSerializer, BarberServiceSerializer
from core.permissions import IsAdminOrManagerOrReadOnly, IsAdminOrManager, IsAdmin, IsManager, IsBarber
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from django.db import transaction

User = get_user_model()

@extend_schema(request=BarberRegisterSerializer)
class BarberRegisterView(CreateAPIView):
    queryset = Barber.objects.all()
    serializer_class = BarberRegisterSerializer
    permission_classes = [IsAdminOrManager]

class BarberViewSet(ModelViewSet):
    serializer_class = BarberSerializer
    permission_classes = [IsAdminOrManagerOrReadOnly]
    http_method_names = ['get', 'patch', 'put', 'head', 'options', 'delete']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Barber.objects.none()

        user = self.request.user

        queryset = Barber.objects.select_related('user', 'branch')

        if user.role == User.Roles.ADMIN:
            return queryset

        if user.role == User.Roles.MANAGER:
            return queryset.filter(branch__manager=user)

        if user.role == User.Roles.BARBER:
            return queryset.filter(user=user)

        return queryset.filter(is_active=True)

    def perform_destroy(self, instance):
        with transaction.atomic():
            instance.is_active = False
            instance.user.is_active = False
            instance.save()
            instance.user.save()

    def perform_update(self, serializer):
        is_active = serializer.validated_data.get('is_active')

        with transaction.atomic():
            barber = serializer.save()

            if is_active is not None:
                barber.user.is_active = is_active
                barber.user.save()


class BarberServiceViewSet(ModelViewSet):
    serializer_class = BarberServiceSerializer
    permission_classes = [IsAdminOrManagerOrReadOnly]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return BarberService.objects.none()

        user = self.request.user
        queryset = BarberService.objects.select_related('barber', 'service')

        if user.role == User.Roles.ADMIN:
            return queryset

        if user.role == User.Roles.MANAGER:
            return queryset.filter(barber__branch__manager=user)

        if user.role == User.Roles.BARBER:
            return queryset.filter(barber__user=user)

        return queryset.filter(barber__is_active=True, service__is_active=True)

class WorkScheduleViewSet(ModelViewSet):
    serializer_class = WorkScheduleSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [(IsAdmin|IsBarber|IsManager)()]
        return [IsAdminOrManager()]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return WorkSchedule.objects.none()

        user = self.request.user
        queryset = WorkSchedule.objects.select_related('barber')

        if user.role == User.Roles.ADMIN:
            return queryset

        if user.role == User.Roles.MANAGER:
            return queryset.filter(barber__branch__manager=user)

        if user.role == User.Roles.BARBER:
            return queryset.filter(barber__user=user)

        return queryset.none()

class TimeOffViewSet(ModelViewSet):
    serializer_class = TimeOffSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [(IsAdmin|IsManager|IsBarber)()]
        return [IsAdminOrManager()]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return TimeOff.objects.none()

        user = self.request.user
        queryset = TimeOff.objects.select_related('barber')

        if user.role == User.Roles.ADMIN:
            return queryset

        if user.role == User.Roles.MANAGER:
            return queryset.filter(barber__branch__manager=user)

        if user.role ==  User.Roles.BARBER:
            return queryset.filter(barber__user=user)

        return queryset.none()