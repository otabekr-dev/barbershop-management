from rest_framework import serializers
from .models import Barber
from apps.services.models import Service

class BarberSerializer(serializers.ModelSerializer):
    services = serializers.PrimaryKeyRelatedField(read_only=True, many=True)

    class Meta:
        model = Barber
        fields = ['id', 'user', 'services', 'is_available']


class BarberAvailabilitySerializer(serializers.ModelSerializer):

    class Meta:
        model = Barber
        fields = ['is_available']


class BarberServiceAssignSerializer(serializers.ModelSerializer):
    services = serializers.PrimaryKeyRelatedField(many=True, queryset=Service.objects.all())

    class Meta:
        model = Barber
        fields = ['services']
        