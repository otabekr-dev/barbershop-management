from django.contrib import admin
from .models import Notification, TelegramLinkToken
admin.site.register([Notification, TelegramLinkToken])