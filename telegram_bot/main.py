import asyncio
from aiogram import Bot, Dispatcher
from decouple import config
from aiohttp import web
from telegram_bot.api.notification import create_app

from telegram_bot.handlers.start import router as start_router

BOT_TOKEN = config('BOT_TOKEN')

async def run_api(bot):
    app = create_app(bot)

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(
        runner,
        host='127.0.0.1',
        port=8080
    )

    await site.start()

    print('Bot HTTP API started on port 8080')

    try:
        await asyncio.Event().wait()
    finally:
        await runner.cleanup()

async def main():
    bot = Bot(BOT_TOKEN)
    dispatcher = Dispatcher()

    dispatcher.include_router(start_router)

    await asyncio.gather(
        dispatcher.start_polling(bot),
        run_api(bot)
    )

if __name__ == '__main__':
    asyncio.run(main())