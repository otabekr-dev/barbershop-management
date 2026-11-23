from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
from rest_framework.decorators import action
from django.contrib.auth import get_user_model

from apps.barbers.models import Barber
from core.permissions import IsAdmin, IsBarber, IsManager

from .serializers import AvailableSlotsQuerySerializer, BookingSerializer, BookingCreateSerializer, BookingCancelSerializer, BookingStatusSerializer
from .service import get_available_slots
from .models import Booking

User = get_user_model()

class AvailableSlotsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(parameters=[AvailableSlotsQuerySerializer])
    def get(self, request:Request, pk:int) -> Response:
        serializer = AvailableSlotsQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        date = serializer.validated_data['date']
        service = serializer.validated_data['service']

        barber = get_object_or_404(Barber, pk=pk)

        slots = get_available_slots(barber=barber, service=service, date=date)

        result = []

        for slot in slots:
            local_slot = timezone.localtime(slot)
            result.append(local_slot.strftime('%H-%M'))

        return Response(result, status=status.HTTP_200_OK)

class BookingViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):

    def get_serializer_class(self):
        if self.action == 'create':
            return BookingCreateSerializer
        if self.action == 'change_status':
            return BookingStatusSerializer
        if self.action == 'cancel':
            return BookingCancelSerializer
        return BookingSerializer

    def get_permissions(self):
        if self.action == 'change_status':
            return [(IsAdmin | IsManager | IsBarber)()]
        return [IsAuthenticated()]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Booking.objects.none()

        user = self.request.user
        queryset = Booking.objects.select_related(
            'barber__user', 'service', 'customer'
        )

        if user.role == User.Roles.ADMIN:
            return queryset
        if user.role == User.Roles.MANAGER:
            return queryset.filter(barber__branch__manager=user)
        if user.role == User.Roles.BARBER:
            return queryset.filter(barber__user=user)
        return queryset.filter(customer=user)

    @action(detail=True, methods=['patch'], url_path='status')
    def change_status(self, request, pk=None):
        booking = self.get_object()

        serializer = self.get_serializer(booking, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        result = BookingSerializer(booking, context=self.get_serializer_context())
        return Response(result.data)

    @action(detail=True, methods=['patch'], url_path='cancel')
    def cancel(self, request, pk=None):
        booking = self.get_object()

        serializer = self.get_serializer(booking, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        result = BookingSerializer(booking, context=self.get_serializer_context())
        return Response(result.data)