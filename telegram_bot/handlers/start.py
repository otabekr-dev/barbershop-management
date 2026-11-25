import aiohttp
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.filters.command import CommandObject
from decouple import config

router = Router()

BOT_SECRET = config('TELEGRAM_BOT_SECRET')
VERIFY_URL = config('DJANGO_VERIFY_URL')

@router.message(CommandStart())
async def start_handler(message:Message, command: CommandObject):
    token = command.args

    if not token:
        await message.answer(
            'Assalomu Alaykum !, Barbershop botimizga xush kelibsiz!'            
        )

    telegram_id = message.from_user.id

    if not VERIFY_URL or not BOT_SECRET:
        await message.answer(
            'Bot konfiguratsiyasida xatolik yuz berdi'
        )

        return

    headers = {
        "X-BOT-SECRET":BOT_SECRET
    }

    payload = {
        'token':token,
        'telegram_id':telegram_id
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                VERIFY_URL,
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:


                data = await response.json()

                if response.status in (200, 201):
                    await message.answer(
                        "Telegram akkauntingiz muvaffaqiyatli ulandi"
                    )
                else:
                    error = data.get('detail', 'No\'malum xatolik')
                    await message.answer(
                        f'Akkauntni ulash amalga oshmadi {error}'
                    )
    except aiohttp.ClientError:
        await message.answer(
            "Server bilan bog\'liq xatolik ro\'y berdi."
        )
    except TimeoutError:
        await message.answer(
            "Server javob bermadi. Keyinroq yana urinib ko'ring"
        )