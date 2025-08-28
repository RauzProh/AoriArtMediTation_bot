from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from tgbot.config import config as cnf

bot = Bot(
    token=cnf.tg_bot.token,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML
    )
)

