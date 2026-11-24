from rest_framework import serializers
from .models import TelegramLinkToken, Notification

class TelegramLinkTokenSerializer(serializers.Serializer):
    token = serializers.CharField()
    bot_link = serializers.URLField()
    expires_at = serializers.DateTimeField()

class TelegramLinkVerifySerializer(serializers.Serializer):
    token = serializers.CharField()
    telegram_id = serializers.IntegerField(min_value=1)
    