from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'id','first_name','last_name',
            'username','email','password',
            'confirm', 'role'
        ]


    def validate(self, attrs):
        if attrs['password'] != attrs['confirm']:
            raise serializers.ValidationError('Parollaringiz mos emas')
        if len(attrs['password']) < 8:
            raise serializers.ValidationError(
                'Parol uzunligi kamida 8-ta elementdan iborat bo\'lishi shart'
            )
        return attrs     

    def create(self, validated_data):
        validated_data.pop('confirm')
        user = User.objects.create_user(**validated_data)
        return user


