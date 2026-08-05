from rest_framework import status
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import ServiceSerializer, Service
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from .permissions import IsBarberOrAdmin

class ServiceView(ListCreateAPIView):
    permission_classes = [IsBarberOrAdmin]
    authentication_classes = [JWTAuthentication]
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer


class ServiceDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsBarberOrAdmin]
    authentication_classes = [JWTAuthentication]
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer