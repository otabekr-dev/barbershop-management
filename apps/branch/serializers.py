from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Branch

User = get_user_model()

class BranchSerializer(serializers.ModelSerializer):

    class Meta:
        model = Branch
        fields = [
            'id', 'name', 'address',
            'phone_number', 'manager',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_manager(self, value):

        if value is None:
            return value

        if value.role != User.Roles.MANAGER:
                raise serializers.ValidationError('Managerning roli MANAGER bo\'lishi shart')
        return value

    def validate(self, attrs):
        user = self.context['request'].user

        if user.role != User.Roles.MANAGER:
            return attrs

        for field in ['manager', 'is_active']:
            if field in attrs:
                raise serializers.ValidationError(
                    'Bu maydonlarni faqatgina Admin o\'zgartirish huquqiga ega'
                )

        return attrs