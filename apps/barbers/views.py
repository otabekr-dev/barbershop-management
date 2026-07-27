from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, UpdateAPIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Barber
from .serializers import BarberSerializer, BarberAvailabilitySerializer, BarberServiceAssignSerializer
from .permissions import IsOwnerBarberOrAdmin, IsAdminRole
from apps.services.permissions import IsBarberOrAdmin


class BarberView(ListCreateAPIView):
    permission_classes = [IsBarberOrAdmin]
    authentication_classes = [JWTAuthentication]
    queryset = Barber.objects.all()
    serializer_class = BarberSerializer

class BarberDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsOwnerBarberOrAdmin]
    authentication_classes = [JWTAuthentication]
    queryset = Barber.objects.all()
    serializer_class = BarberSerializer

class BarberAvailabilityView(UpdateAPIView):
    permission_classes = [IsOwnerBarberOrAdmin]
    authentication_classes = [JWTAuthentication]
    queryset = Barber.objects.all()
    serializer_class = BarberAvailabilitySerializer

class BarberAssignServiceView(UpdateAPIView):
    permission_classes = [IsAdminRole]
    authentication_classes = [JWTAuthentication]
    queryset = Barber.objects.all()
    serializer_class = BarberServiceAssignSerializer
        