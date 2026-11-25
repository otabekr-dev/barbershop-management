import secrets
import hashlib
from datetime import timedelta

from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework.exceptions import PermissionDenied, ValidationError
from decouple import config

from .models import TelegramLinkToken

User = get_user_model()

TELEGRAM_BOT_USERNAME = config('TELEGRAM_BOT_USERNAME')


@transaction.atomic
def create_telegram_link_token(user):
    if user.role not in [
        User.Roles.ADMIN,
        User.Roles.BARBER,
        User.Roles.MANAGER
    ]:
        raise PermissionDenied(
            'Telegram akkauntini faqat administrator, filial menejeri va sartaroshlar bog\'lashi mumkin.'
        )

    if user.telegram_id:
        raise ValidationError(
            'Telegram akkauntingiz allaqachon bog\'langan.'
        )

    TelegramLinkToken.objects.filter(
        user=user,
        used_at__isnull=True
    ).delete()

    raw_token = secrets.token_urlsafe(32)

    token_hash = hashlib.sha256(
        raw_token.encode('utf-8')
    ).hexdigest()

    expires_at = timezone.now() + timedelta(minutes=5)

    TelegramLinkToken.objects.create(
        user=user,
        token_hash=token_hash,
        expires_at=expires_at
    )

    bot_link = (
        f'https://t.me/{TELEGRAM_BOT_USERNAME}?start={raw_token}'
    )

    return {
        'token': raw_token,
        'bot_link': bot_link,
        'expires_at': expires_at
    }


@transaction.atomic
def verify_telegram_link_token(raw_token, telegram_id):
    token_hash = hashlib.sha256(
        raw_token.encode('utf-8')
    ).hexdigest()

    link_token = (
        TelegramLinkToken.objects
        .select_for_update()
        .select_related('user')
        .filter(token_hash=token_hash)
        .first()
    )

    if not link_token:
        raise ValidationError('Token noto\'g\'ri yoki mavjud emas.')

    if link_token.used_at is not None:
        raise ValidationError('Bu token allaqachon ishlatilgan.')

    if link_token.expires_at <= timezone.now():
        raise ValidationError('Tokenning amal qilish muddati tugagan.')

    user = link_token.user

    if user.role not in [
        User.Roles.ADMIN,
        User.Roles.MANAGER,
        User.Roles.BARBER
    ]:
        raise PermissionDenied(
            'Bu akkauntni Telegram bilan bog\'lashga ruxsat yo\'q.'
        )

    if user.telegram_id is not None:
        raise ValidationError(
            'Telegram akkauntingiz allaqachon bog\'langan.'
        )

    if User.objects.filter(telegram_id=telegram_id).exists():
        raise ValidationError(
            'Bu Telegram akkaunti boshqa foydalanuvchiga bog\'langan.'
        )

    user.telegram_id = telegram_id
    user.save(update_fields=['telegram_id', 'updated_at'])

    link_token.used_at = timezone.now()
    link_token.save(update_fields=['used_at'])

    return user
