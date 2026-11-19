import secrets

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from rest_framework import serializers

from apps.branch.models import Branch
from apps.service.models import Service
from core.validators import validate_uzb_numbers
from core.utils import generate_password
from .models import Barber, BarberService, TimeOff, WorkSchedule

User = get_user_model()


def get_value(serializer, attrs, name):
    if name in attrs:
        return attrs[name]
    if serializer.instance is not None:
        return getattr(serializer.instance, name)
    return None


class BarberRegisterSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    phone_number = serializers.CharField(
        max_length=13,
        validators=[validate_uzb_numbers],
    )
    branch = serializers.PrimaryKeyRelatedField(
        queryset=Branch.objects.filter(is_active=True)
    )
    experience_years = serializers.IntegerField(min_value=0, default=0)
    bio = serializers.CharField(allow_blank=True, default='')

    def validate_phone_number(self, value):
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError(
                'Bu raqam boshqa user tomonidan ishlatilmoqda'
            )
        return value

    def validate_branch(self, value):
        user = self.context['request'].user
        if user.role == User.Roles.MANAGER and value.manager_id != user.id:
            raise serializers.ValidationError(
                'Siz faqat o\'z filialingizga sartarosh qo\'sha olasiz'
            )
        return value

    def create(self, validated_data):
        password = generate_password()

        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    first_name=validated_data['first_name'],
                    last_name=validated_data['last_name'],
                    phone_number=validated_data['phone_number'],
                    password=password,
                    role=User.Roles.BARBER,
                )

                barber = Barber.objects.create(
                    user=user,
                    branch=validated_data['branch'],
                    bio=validated_data.get('bio', ''),
                    experience_years=validated_data['experience_years'],
                )
        except IntegrityError:
            raise serializers.ValidationError(
                'Ro\'yxatdan o\'tkazilmadi, yana harakat qilib ko\'ring.'
            )

        barber.generated_password = password
        return barber

    def to_representation(self, instance):
        return {
            'id': instance.id,
            'first_name': instance.user.first_name,
            'last_name': instance.user.last_name,
            'phone_number': instance.user.phone_number,
            'branch': instance.branch_id,
            'experience_years': instance.experience_years,
            'bio': instance.bio,
            'password': getattr(instance, 'generated_password', None),
        }


class BarberSerializer(serializers.ModelSerializer):

    class Meta:
        model = Barber
        fields = [
            'id', 'user', 'branch',
            'bio', 'experience_years',
            'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

class BarberServiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = BarberService
        fields = [
            'id', 'barber', 'service',
            'custom_price', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_custom_price(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError(
                'Narx noldan katta bo\'lishi kerak.'
            )
        return value

    def validate_service(self, value):
        if not value.is_active:
            raise serializers.ValidationError('Bu xizmat faol emas')
        return value

    def validate_barber(self, value):
        user = self.context['request'].user

        if not value.is_active:
            raise serializers.ValidationError('Faol bo\'lmagan sartaroshga xizmat biriktirib bo\'lmaydi')

        if user.role == User.Roles.ADMIN:
            return value

        if user.role == User.Roles.MANAGER:
            if value.branch.manager_id != user.id:
                raise serializers.ValidationError(
                    'Siz faqat o\'z filialingiz sartaroshlari uchun yoza olasiz'
                )
            return value

        raise serializers.ValidationError('Sizda bu amal uchun ruxsat yo\'q')
    

class WorkScheduleSerializer(serializers.ModelSerializer):

    class Meta:
        model = WorkSchedule
        fields = [
            'id', 'barber', 'weekday',
            'start_time', 'end_time', 'break_start',
            'break_end', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, attrs):
        start_time = get_value(self, attrs, 'start_time')
        end_time = get_value(self, attrs, 'end_time')
        break_start = get_value(self, attrs, 'break_start')
        break_end = get_value(self, attrs, 'break_end')

        if start_time is not None and end_time is not None:
            if end_time <= start_time:
                raise serializers.ValidationError(
                    'Ish tugashi boshlanishidan keyin bo\'lishi kerak'
                )

        if (break_start is None) != (break_end is None):
            raise serializers.ValidationError(
                'Tanaffusning boshlanishi va tugashi birga kiritilishi shart'
            )

        if break_start is not None:
            if break_end <= break_start:
                raise serializers.ValidationError(
                    'Tanaffusning tugash vaqti boshlanishidan keyin bo\'lishi kerak'
                )

            if start_time is not None and end_time is not None:
                if break_start < start_time or break_end > end_time:
                    raise serializers.ValidationError(
                        'Tanaffus ish vaqtining ichida bo\'lishi shart'
                    )

        return attrs

    def validate_barber(self, value):
        user = self.context['request'].user

        if not value.is_active:
            raise serializers.ValidationError('Faol bo\'lmagan sartaroshga ish vaqti belgilab bo\'lmaydi')
        

        if user.role == User.Roles.ADMIN:
            return value

        if user.role == User.Roles.MANAGER:
            if value.branch.manager_id != user.id:
                raise serializers.ValidationError(
                    'Siz faqat o\'z filialingiz sartaroshlari uchun yoza olasiz'
                )
            return value

        raise serializers.ValidationError('Sizda bu amal uchun ruxsat yo\'q')


class TimeOffSerializer(serializers.ModelSerializer):

    class Meta:
        model = TimeOff
        fields = [
            'id', 'barber', 'start_date',
            'end_date', 'reason', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, attrs):
        start_date = get_value(self, attrs, 'start_date')
        end_date = get_value(self, attrs, 'end_date')

        if start_date is not None and end_date is not None:
            if end_date < start_date:
                raise serializers.ValidationError(
                    'Tugash sanasi boshlanish sanasidan oldin bo\'lmaydi'
                )

        return attrs

    def validate_barber(self, value):
        user = self.context['request'].user

        if not value.is_active:
            raise serializers.ValidationError('Faol bo\'lmagan sartaroshga ta\'til belgilab bo\'lmaydi')


        if user.role == User.Roles.ADMIN:
            return value

        if user.role == User.Roles.MANAGER:
            if value.branch.manager_id != user.id:
                raise serializers.ValidationError(
                    'Siz faqat o\'z filialingiz sartaroshlari uchun yoza olasiz'
                )
            return value

        raise serializers.ValidationError('Sizda bu amal uchun ruxsat yo\'q')