from aiogram.filters import BaseFilter
from aiogram.types import Message

from database.PostgreSQL import DatabasePSQL
from tgbot.config import Config


class BuyerFilter(BaseFilter):
    async def __call__(self, obj: Message, db_session: DatabasePSQL, config: Config) -> bool:
        return await db_session.get_accesses(obj.from_user.id)
