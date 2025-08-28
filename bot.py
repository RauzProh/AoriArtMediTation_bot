import asyncio
import logging

import betterlogging as bl
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.base import DefaultKeyBuilder
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage

from database.PostgreSQL import DatabasePSQL

from tgbot.config import load_config, Config

from tgbot.middlewares.config import ConfigMiddleware

from tgbot.middlewares.database import DatabaseMiddleware
from tgbot.misc.check_server import WebhookReader
from tgbot.misc.set_bot_commands import set_default_commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from tgbot.keyboards.inline import scenario_uodate
from datetime import datetime, timedelta
# from database.PostgreSQL import
import types

from web.web_server import app

scheduler = AsyncIOScheduler()

# async def send_offline_reminder(bot: Bot, db: DatabasePSQL, user_id: int, step: int):
#     if await db.is_purchased(user_id):
#         return  # человек уже купил билет → не шлем уведомлени
#     # Получаем данные пользователя из БД
#     user = await db.get_user_from_db(user_id)
#     if not user:
#         return

#     if user["buttons_clicked"]:
#         return  # не отправляем, если юзер сам нажал "напомнить позже"

#     text = ""
#     buttons = None

#     if step == 0:  # Через 2 дня после покупки
#         text = ("Приглашаю тебя в новое путешествие. На этот раз вживую.\n\n"
#                 "Через самую дорогую картину — 'Спаситель мира'\n"
#                 "ХХ сентября, хх:хх, Москва")
#         buttons = types.InlineKeyboardMarkup()
#         buttons.add(types.InlineKeyboardButton(text="купить билет", url="https://paylink.ru/4900"))
#         buttons.add(types.InlineKeyboardButton(text="расскажи подробнее", callback_data="details"))
#         buttons.add(types.InlineKeyboardButton(text="напомните позже", callback_data="remind_later"))

#     elif step == 1:  # +3 часа
#         text = ("Арт-медиация — формат для тех, кто хочет глубины. "
#                 "Это не лекция, а обсуждение, исследование через искусство.")

#     elif step == 2:  # +24 часа
#         text = ("Встреча, которую я готовлю, не похожа на стандартный формат. "
#                 "Ты не слушатель. Ты — участник, исследователь, зритель.")

#     elif step == 3:  # +48 часов
#         text = ("У этой встречи не будет записи. Это поле рождается только раз. "
#                 "Количество мест ограничено.")

#     if text:
#         await bot.send_message(user_id, text, reply_markup=buttons)

#         # фиксируем в БД, что напоминание отправлено
#         await db.update_last_sent(user_id, datetime.now(), step)


# def schedule_offline_reminders(bot: Bot, db: DatabasePSQL, user_id: int, purchase_time: datetime):
#     """
#     Добавляем задания для пользователя в планировщик.
#     """
#     scheduler.add_job(send_offline_reminder, "date",
#                       run_date=purchase_time + timedelta(days=2),
#                       args=[bot, db, user_id, 0])

#     scheduler.add_job(send_offline_reminder, "date",
#                       run_date=purchase_time + timedelta(days=2, hours=3),
#                       args=[bot, db, user_id, 1])

#     scheduler.add_job(send_offline_reminder, "date",
#                       run_date=purchase_time + timedelta(days=3, hours=2),
#                       args=[bot, db, user_id, 2])

#     scheduler.add_job(send_offline_reminder, "date",
#                       run_date=purchase_time + timedelta(days=4, hours=2),
#                       args=[bot, db, user_id, 3])



async def reminder_worker(bot, db):
    try:
        while True:
            # print("Проверка напоминаний")
            now = datetime.utcnow()
            sql = """
            SELECT id, user_id, type, payload FROM reminders
            WHERE status = 'pending' AND send_at <= $1
            """
            rows = await db.execute(sql, now, fetch=True)

            for row in rows:
                user_id = row['user_id']
                reminder_type = row['type']
                payload = row['payload']

                # отправка напоминания
                await send_reminder(bot, user_id, reminder_type, payload)

                # помечаем как отправленное
                await db.execute("UPDATE reminders SET status='sent' WHERE id=$1", row['id'], execute=True)

            await asyncio.sleep(10)  # проверка каждые 10 секунд
    except Exception as e:
        print(f"Ошибка при добавлении доступа: {e}") 


async def send_reminder(bot, user_id, reminder_type, payload):
    if reminder_type == "firstpay":
        await bot.send_message(user_id, "Я здесь, чтобы напомнить: твое личное аудио-погружение в свой мир через шедевр\n\n\
Возрождения тебя ждет. Возможно, сейчас — то самое время", reply_markup = await scenario_uodate.after_feedback())
    elif reminder_type == 'email':
        await bot.send_message(user_id, "Я буду рада выслать вам аудио-погружение сразу, как только вы напишете свой e-mail")
    elif reminder_type == 'email24':
        await bot.send_message(user_id, "Возможность получить подарок почти ускользнула...\n\n\
Оставь свой e-mail, и я смогу отправить тебе то, что подготовила специально для тебя 💌")
    elif reminder_type == 'start':
        await bot.send_message(user_id, "Я здесь, чтобы напомнить: твое личное аудио-погружение в свой мир через шедевр\n\n\
Возрождения тебя ждет. Возможно, сейчас — то самое время", reply_markup=await scenario_uodate.reminder_start_btn())
    elif reminder_type == 'start24':
        await bot.send_message(user_id, "Прошёл целый день, а твое личное аудио-погружение всё ещё ждёт тебя.\n\n\
Шедевр Возрождения откроется только тем, кто решится войти. Может, сейчас — именно твой момент?", reply_markup=await scenario_uodate.reminder_start_btn())
    elif reminder_type == 'choice_audio':
        await bot.send_message(user_id, "Я здесь, чтобы напомнить: твое личное аудио-погружение в свой мир через шедевр\n\n\
Возрождения тебя ждет. Возможно, сейчас — то самое время", reply_markup=await scenario_uodate.audio_choice_step())
    elif reminder_type == 'choice_audio24':
        await bot.send_message(user_id, "Прошёл целый день, а твое личное аудио-погружение всё ещё ждёт тебя.\n\n\
Шедевр Возрождения откроется только тем, кто решится войти. Может, сейчас — именно твой момент?", reply_markup=await scenario_uodate.audio_choice_step())
    elif reminder_type == 'choice_audio_reminder':
        await bot.send_message(user_id, "“помнишь, дорога к своим открытиям вместе с великим гением нас ждет?", reply_markup=await scenario_uodate.continue_now())
    elif reminder_type == 'first_audio':
        await bot.send_message(user_id, "Я здесь, чтобы напомнить: твое личное аудио-погружение в свой мир через шедевр\n\n\
Возрождения тебя ждет. Возможно, сейчас — то самое время", reply_markup=await scenario_uodate.continue_step())
    elif reminder_type == 'after_audio':
        await bot.send_message(user_id, "Тебе понравилась дорога в свою глубину?", reply_markup=await scenario_uodate.continue_step())
    elif reminder_type == 'after_audio3':
        await bot.send_message(user_id, "Я здесь, чтобы напомнить: твое личное аудио-погружение в свой мир через шедевр\n\n\
Возрождения тебя ждет. Возможно, сейчас — то самое время", reply_markup=await scenario_uodate.continue_step())
    elif reminder_type == 'after_audio24':
        await bot.send_message(user_id, "Прошёл целый день, а твое личное аудио-погружение всё ещё ждёт тебя.\n\n\
Шедевр Возрождения откроется только тем, кто решится войти. Может, сейчас — именно твой момент?", reply_markup=await scenario_uodate.continue_step())
    elif reminder_type == 'after_pay':
        await bot.send_message(user_id, "Приглашаю тебя в новое путешествие. На этот раз вживую.\n\n\
Поговорить с Леонардо о поиске своей целостности, как ориентироваться в мире, где нет\
ничего определенного, как оставаться в нем устойчивым. Через самую дорогую картину,\
когда либо проданных картин: “Спаситель мира\n\n”\
Пропустить размышления гения сквозь себя и увидеть собственные ответы\n\n\
ХХ сентября, хх:хх, Москва\n\n\
Это не аудио. Не бот. Это — живое пространство разговора в камерной и доверительной\
атмосфере", reply_markup=await scenario_uodate.offline_event_step())
    
    


    # if reminder_type == "track_reminder":
    #     await bot.send_message(user_id, "Не забудь продолжить аудио-погружение!")
    # elif reminder_type == "email_reminder":
    #     await bot.send_message(user_id, "Пожалуйста, оставь свой e-mail, чтобы получить подарок!")
    # elif reminder_type.startswith("offline_event"):
    #     await bot.send_message(user_id, "Не пропусти оффлайн-событие!")


def register_global_middlewares(dp: Dispatcher, config: Config, session_pool=None):
    middleware_types = [
        ConfigMiddleware(config)
    ]

    if session_pool:
        middleware_types.append(DatabaseMiddleware(session_pool))
        dp.update.outer_middleware(DatabaseMiddleware(session_pool))

    for middleware_type in middleware_types:
        dp.message.outer_middleware(middleware_type)
        dp.callback_query.outer_middleware(middleware_type)


def setup_logging():
    log_level = logging.INFO
    bl.basic_colorized_config(level=log_level)

    logging.basicConfig(
        level=logging.INFO,
        format="%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s",
    )
    logger = logging.getLogger(__name__)
    logger.info("Starting bot")


def get_storage(config):
    if config.tg_bot.use_redis:
        return RedisStorage.from_url(
            config.redis.dsn(),
            key_builder=DefaultKeyBuilder(with_bot_id=True, with_destiny=True),
        )
    else:
        return MemoryStorage()


async def on_startup(bot: Bot, admin_ids: list[int]):
    await set_default_commands(bot, admin_ids)
    # await broadcaster.broadcast(bot, admin_ids, "Бот запущен!")


async def db_psql(config):
    db = DatabasePSQL(config.db)
    # await db.drop_users()
    # await db.drop_tickets()
    # await db.drop_impressions()
    # await db.drop_accesses()
    # await db.drop_payments()

    await db.create_table_users()
    await db.create_table_tickets()
    await db.create_table_impressions()
    await db.create_table_payments()
    await db.create_table_accesses()
    await db.create_table_promocode()
    await db.create_table_offline_reminders()
    await db.create_table_reminders()

    return db


async def main():
    from tgbot.handlers import routers_list
    # app.run(host="0.0.0.0", port=8093)

    setup_logging()

    config = load_config(".env")
    storage = get_storage(config)

    bot = Bot(token=config.tg_bot.token,
              default=DefaultBotProperties(parse_mode="HTML", protect_content=True))
    dp = Dispatcher(storage=storage)
    dp.include_routers(*routers_list)

    db = await db_psql(config)

    register_global_middlewares(dp, config, db)
    asyncio.create_task(WebhookReader.reader(db))  # приём платежей

    # <<< ЗАПУСКАЕМ reminder_worker >>>
    asyncio.create_task(reminder_worker(bot, db))

    # <<< ЗАПУСКАЕМ APSCHEDULER >>>
    scheduler.start()
    
    print('Запуск бота')
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.error("Бот остановлен!")
