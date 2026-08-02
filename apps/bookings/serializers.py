from rest_framework import serializers
from django.db.models import Q
from .models import Booking, Barber, Service
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
User = get_user_model()

class BookingSerializer(serializers.ModelSerializer):
    customer = serializers.PrimaryKeyRelatedField(read_only=True)
    status = serializers.CharField(read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'customer', 'barber',
            'service', 'date','start_time', 'status',
            'created_at'
        ]

    def validate(self, attrs):
        barber = attrs['barber']
        date = attrs['date']
        start_time = attrs['start_time']
        service = attrs['service']


        request = self.context['request']

        if barber.user == request.user:
            raise serializers.ValidationError("O'zingizga booking qila olmaysiz")

        new_start = datetime.combine(date, start_time)
        new_end = new_start + service.duration

        existing_books = Booking.objects.filter(
            barber=barber, date=date
        ).exclude(status="CANCELLED")

        if self.instance:
            existing_books = existing_books.exclude(id=self.instance.id)

        for booking in existing_books:
            existing_start = datetime.combine(booking.date, booking.start_time)
            existing_end = existing_start + booking.service.duration 

            if new_start < existing_end and  new_end > existing_start:
                raise serializers.ValidationError('Bu vaqt oralig\'ida sartarosh band')

        
        return attrs        


class BookingStatusSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Booking
        fields = ['status']
