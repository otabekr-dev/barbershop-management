from django.urls import path
from .views import TelegramLinkTokenView, TelegramVerifyView

urlpatterns = [
    path('telegram/link/', TelegramLinkTokenView.as_view(), name='telegram_link'),
    path('telegram/verify/', TelegramVerifyView.as_view(), name='telegram_verify')
]
