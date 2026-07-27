from rest_framework import serializers
from .models import Service


class ServiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Service
        fields = [
            'id', 'name',
            'price', 'duration'
        ]


    def validate_name(self, value):
        data = value.strip().lower()
        service = Service.objects.filter(name__iexact=data)
        if service:
            raise serializers.ValidationError('Mavjud xizmat')    
        return value