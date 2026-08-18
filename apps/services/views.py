from django.core.cache import cache
from rest_framework import status
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import ServiceSerializer, Service
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from .permissions import IsBarberOrAdmin
from django.conf import settings

class ServiceView(ListCreateAPIView):
    permission_classes = [IsBarberOrAdmin]
    authentication_classes = [JWTAuthentication]
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

    def list(self, request, *args, **kwargs):
        cached_services = cache.get("services_list")

        if cached_services is not None:
            return Response(cached_services)

        response = super().list(request, *args, **kwargs)

        cache.set("services_list", response.data, settings.CACHE_TIMEOUT)

        print(cache.get("services_list"))
        
        return response

    def perform_create(self, serializer):
        serializer.save()
        cache.delete("services_list")

class ServiceDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsBarberOrAdmin]
    authentication_classes = [JWTAuthentication]
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer


    def perform_update(self, serializer):
        serializer.save()
        cache.delete("services_list")


    def perform_destroy(self, instance):
        instance.delete()
        cache.delete("services_list")    