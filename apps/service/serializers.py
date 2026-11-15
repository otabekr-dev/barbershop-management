from rest_framework import serializers
from .models import Service


class ServiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Service
        fields = [
            'id', 'name', 'description',
            'price', 'duration', 'is_active',
            'created_at', 'updated_at'
        ]   
        read_only_fields = [
            'id', 'created_at', 'updated_at'
        ]

    def validate_name(self, value):
        value = ' '.join(value.split()) 

        queryset = Service.objects.filter(name__iexact=value)

        if self.instance is not None:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise serializers.ValidationError('Bu nomli servis mavjud')  

        return value