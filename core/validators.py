from django.core.exceptions import ValidationError
from decouple import config

MAX_SERVICE_SECONDS = config('MAX_SERVICE_SECONDS', cast=int)

def validate_uzb_numbers(value):
    if len(value) != 13:
        raise ValidationError('Telefon raqamingizni to\'g\'ri kiriting: Masalan :(+998991234567)')
    if not value.startswith('+998'):
        raise ValidationError('Telefon raqamingizni to\'g\'ri kiriting: Masalan :(+998991234567)')
    if not value[1:].isdigit():
        raise ValidationError('Telefon raqami raqamlardan tashkil topgan bo\'lishi shart')

    return value

def validate_service_duration(value):
    seconds = value.total_seconds()

    if seconds <=0:
        raise ValidationError('Servis davomiyligi 1 daqiqadan katta bo\'lishi kerak')

    if seconds > MAX_SERVICE_SECONDS:
        raise ValidationError('Servis davomiyligi 8 soatdan oshishi mumkin emas')
    
    if seconds % 1800 != 0:
        raise ValidationError('Servis davomiyligi 30 daqiqaga karrali bo\'lishi kerak')


    return value 