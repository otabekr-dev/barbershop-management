from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm = serializers.CharField(write_only=True)


    class Meta:
        model = User
        fields = [
            'id', 'first_name', 'last_name',
            'phone_number','password','confirm'
        ]


    def validate(self, attrs):
        if attrs['password'] != attrs['confirm']:
            raise serializers.ValidationError('Parollar mos emas')
        if len(attrs['password']) < 8:
            raise serializers.ValidationError('Parol uzunligi minimum 8 ta elementdan iborat bo\'lishi kerak')

        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm')
        user = User.objects.create_user(**validated_data)
        return user

class MeSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'phone_number', 'role']

class StaffCreateSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(
        choices = [
            (User.Roles.MANAGER, 'Manager'),
            (User.Roles.BARBER, 'Barber')
        ]
    )

    class Meta:
        model = User
        fields = ['id', 'phone_number', 'first_name','last_name','password','role']
        extra_kwargs = {'password':{'write_only':True}}

    def create(self, validated_data):
        password = validated_data.pop('password')

        return User.objects.create_user(password=password, **validated_data)
    