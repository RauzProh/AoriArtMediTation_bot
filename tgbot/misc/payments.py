import asyncio
import logging
from datetime import datetime

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.types import FSInputFile
from yookassa import Payment, Configuration
from yookassa.domain.notification import WebhookNotification

from tgbot.config import load_config
from tgbot.keyboards.inline.scenario_keyboards import step_7
from tgbot.services.broadcaster import send_message, send_message_audio

config = load_config(".env")
bot = Bot(token=config.tg_bot.token, default=DefaultBotProperties(parse_mode='HTML', protect_content=True))
Configuration.account_id = config.tg_bot.yookassa_id
Configuration.secret_key = config.tg_bot.yookassa_key


async def notification_payment(event_json, db):
    notification_object = WebhookNotification(event_json)
    print(f"{notification_object=}")
    payment = notification_object.object
    if payment.test is False:
        return
    print(f"{payment=}")
    payment_id = payment.id
    status = payment.status
    db_payment = await db.get_payment(payment_id)
    print(f"{db_payment=}")

    if not db_payment or status == db_payment.get('status'):
        return

    telegram_id = db_payment.get('user_id')

    if status == 'succeeded':
        date = datetime.now()
        await db.update_payment_status(payment_id, status, date)

        if db_payment.get('gift'):
            ticket = int(datetime.now().timestamp())
            await db.add_ticket(telegram_id, ticket)
            username_bot = (await bot.get_me()).username
            link = f'https://t.me/{username_bot}?start={ticket}'
            text = f'Пригласи друга в бота передав ему эту ссылку: {link}'
            await send_message(bot, telegram_id, text, protect_content=False)
            return

        await db.add_accesses(telegram_id)
        text = (f"Теперь все готово.\nУстраивайся поудобнее, настраивайся на неспешный темп, включай аудио"
                f" и следуй за моим голосом")

        audio = FSInputFile("media/Настройся.mp3")
        await send_message(bot, telegram_id, text)
        await send_message_audio(bot, telegram_id, text='', audio=audio, reply_markup=await step_7())

    elif status == 'canceled':
        await db.update_payment_status(payment_id, status)

    else:
        logging.warning(f'Неизвестный статус платежа:{event_json=}')


async def create_payment(amount, email, gift):
    # Создание платежа
    payment = Payment.create({
        "amount": {
            "value": amount,
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://t.me/AoriArtMediTation_bot"
        },
        "metadata": {
            'gift': gift
        },
        "capture": True,
        "description": "Оплата доступа к материалам",
        "receipt": {
            "customer": {
                "email": email
            },

            "items": [
                {
                    "description": "Оплата доступа к материалам",
                    "quantity": "1",
                    "amount": {
                        "value": amount,
                        "currency": "RUB"
                    },
                    "vat_code": "1",
                    "payment_mode": "full_payment",
                    "payment_subject": "service",
                }

            ]
        }
    })

    return payment.id, payment.confirmation.confirmation_url


async def check_oplata(pay_id):
    payment = Payment.find_one(pay_id)
    return payment.status