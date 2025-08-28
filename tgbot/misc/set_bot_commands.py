from aiogram import types
from aiogram.types import BotCommandScopeAllPrivateChats, BotCommandScopeChat


async def set_default_commands(bot, admin_ids: list[int]):
    print(admin_ids)
    await bot.set_my_commands(
        [
            types.BotCommand(command="start", description="Включить бота"),

        ], scope=BotCommandScopeAllPrivateChats()

    )

    for admin_id in admin_ids:
        print(admin_id)
        await bot.set_my_commands([
            types.BotCommand(command="start", description="Включить бота"),
            types.BotCommand(command="get_data", description="Выгрузить все объявления"),
            types.BotCommand(command="promocode", description="Создать промокод"),
        ], scope=BotCommandScopeChat(chat_id=int(admin_id)))
