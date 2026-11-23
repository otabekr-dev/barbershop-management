from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import Booking
from apps.service.models import Service
from apps.barbers.models import BarberService
from .service import create_booking

User = get_user_model()

ALLOWED_TRANSITIONS = {
    Booking.StatusChoice.PENDING: [Booking.StatusChoice.CONFIRMED],
    Booking.StatusChoice.CONFIRMED : [
        Booking.StatusChoice.COMPLETED,
        Booking.StatusChoice.NO_SHOW
    ]
}

class AvailableSlotsQuerySerializer(serializers.Serializer):
    date = serializers.DateField()
    service = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.filter(is_active=True)
    )


    def validate_date(self, value):
        if value < timezone.localdate():
            raise serializers.ValidationError(
                'O\'tib ketgan sanani tanlab bo\'lmaydi'
            )
        return value

class BookingSerializer(serializers.ModelSerializer):
    barber_name = serializers.CharField(source='barber.user.first_name', read_only=True)
    service_name = serializers.CharField(source='service.name', read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'customer', 'guest_name', 'guest_phone',
            'barber', 'barber_name', 'service', 'service_name',
            'start_at', 'end_at', 'price', 'status', 'note',
            'cancelled_by', 'cancelled_reason',
            'created_at', 'updated_at',
        ]
        read_only_fields = fields

class BookingCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Booking
        fields = ['barber', 'service', 'start_at', 'note', 'guest_name', 'guest_phone']

    def validate_start_at(self, value):
        if value <=timezone.now():
            raise serializers.ValidationError('O\'tib ketga vaqtga yozilib bo\'lmaydi')
        return value

    def validate_service(self, value):
        if not value.is_active:
            raise serializers.ValidationError('Bu xizmat hozir mavjud emas')
        return value

    def validate_barber(self, value):
        user = self.context['request'].user

        if not value.is_active:
            raise serializers.ValidationError('Bu sartarosh hozir ishlamaydi')

        
        if user.role == User.Roles.BARBER and value.user_id != user.id:
            raise serializers.ValidationError('Siz faqat o\'zingizga yoza olasiz')

        
        if user.role == User.Roles.MANAGER and value.branch.manager_id != user.id:
            raise serializers.ValidationError(
                'Siz faqat o\'z filialingiz sartaroshlariga yoza olasiz'
            )

        return value

    def validate(self, attrs):
        user = self.context['request'].user

        pair_exists = BarberService.objects.filter(
            barber=attrs['barber'],
            service=attrs['service'],
        ).exists()

        if not pair_exists:
            raise serializers.ValidationError('Bu sartaroshda bu xizmat mavjud emas')

        if user.role == User.Roles.CUSTOMER:

            attrs['guest_name'] = ''
            attrs['guest_phone'] = ''

        else:

            if not attrs.get('guest_phone'):
                raise serializers.ValidationError('Guest telefoni majburiy')

        return attrs

    def create(self, validated_data):
        user = self.context['request'].user

        if user.role == User.Roles.CUSTOMER:
            customer = user
        else:
            customer = None

        return create_booking(
            barber=validated_data['barber'],
            service=validated_data['service'],
            start_at=validated_data['start_at'],
            customer=customer,
            guest_name=validated_data.get('guest_name', ''),
            guest_phone=validated_data.get('guest_phone', ''),
            note=validated_data.get('note', '')
        )

    def to_representation(self, instance):
        return BookingSerializer(instance, context=self.context).data

class BookingStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=[   
            (Booking.StatusChoice.CONFIRMED, 'Tasdiqlandi'),
            (Booking.StatusChoice.COMPLETED, 'Bajarildi'),
            (Booking.StatusChoice.NO_SHOW, 'Kelmadi'),
        ]
    )

    def validate_status(self, value):

        current = self.instance.status
        allowed = ALLOWED_TRANSITIONS.get(current, [])

        if value not in allowed:
            raise serializers.ValidationError(
                f'{current} holatdan {value}ga o\'tib bo\'lmaydi'
            )

        finished = [
            Booking.StatusChoice.COMPLETED,
            Booking.StatusChoice.NO_SHOW,
        ]

        if value in finished and self.instance.start_at > timezone.now():
            raise serializers.ValidationError('Booking vaqti kelmagunicha bu holatni belgilab bo\'lmaydi')

        return value

    def update(self, instance, validated_data):
        instance.status = validated_data['status']

        instance.save(update_fields=['status', 'updated_at'])
        return instance 

class BookingCancelSerializer(serializers.Serializer):
    cancelled_reason = serializers.CharField(required=False, allow_blank=True, default='')

    def validate(self, attrs):
        booking = self.instance

        cancellable = [
            Booking.StatusChoice.PENDING,
            Booking.StatusChoice.CONFIRMED
        ]

        if booking.status not in cancellable:
            raise serializers.ValidationError('Bu bookingni bekor qilib bo\'lmaydi')

        if booking.start_at <= timezone.now():
            raise serializers.ValidationError(
                'Vaqti o\'tib ketgan bookingni bekor qilib bo\'lmaydi'
            ) 

        return attrs


    def update(self, instance, validated_data):
        instance.status = Booking.StatusChoice.CANCELLED
        instance.cancelled_by = self.context['request'].user
        instance.cancelled_reason = validated_data.get('cancelled_reason', '')
        instance.save(
            update_fields = [
                'status', 'cancelled_by', 'cancelled_reason', 'updated_at'
            ]
        )
        return instance