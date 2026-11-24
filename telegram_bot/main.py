import asyncio
from aiogram import Bot, Dispatcher
from decouple import config

from telegram_bot.handlers.start import router as start_router

BOT_TOKEN = config('BOT_TOKEN')

async def main():
    bot = Bot(BOT_TOKEN)
    dispatcher = Dispatcher()

    dispatcher.include_router(start_router)

    await dispatcher.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())