from decouple import config
import secrets

PASSWORD_ALPHABET = config('PASSWORD_ALPHABET')
PASSWORD_LENGTH = config('PASSWORD_LENGTH', cast=int)


def generate_password():
    password = ''
    for _ in range(PASSWORD_LENGTH):
        password += secrets.choice(PASSWORD_ALPHABET)
    return password