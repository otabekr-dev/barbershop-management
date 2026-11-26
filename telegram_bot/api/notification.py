import secrets
from decouple import config
from aiohttp import web
from aiogram import Bot
from aiogram.exceptions import TelegramAPIError

async def send_notification_handler(request: web.Request):
    bot: Bot = request.app['bot']

    expected_secret = config('TELEGRAM_BOT_SECRET')
    received_secret = request.headers.get('X-BOT-SECRET', '')

    if not expected_secret or not secrets.compare_digest(
        expected_secret, received_secret
    ):
        raise web.HTTPUnauthorized(text='Invalid bot secret')

    try:
        data = await  request.json()
    except(ValueError, web.HTTPBadRequest):
        raise web.HTTPBadRequest(text='Invalid JSON')

    telegram_id = data.get('telegram_id')
    message = data.get('message')

    if not isinstance(telegram_id, int) or not isinstance(message, str) or not message.strip():
        raise web.HTTPBadRequest(text='Invalid notification data')

    try:
        await bot.send_message(
            chat_id=telegram_id,
            text=message
        )
    except TelegramAPIError:
        return web.json_response(
            {"ok":False, "detail":"Telegram message could not be sent"},
            status=502
        )

    return web.json_response({"ok":True})

def create_app(bot:Bot):
    app = web.Application()

    app['bot'] = bot

    app.router.add_post(
        '/notifications/send/',
        send_notification_handler
    )

    return app