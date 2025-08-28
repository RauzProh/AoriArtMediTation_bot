import re

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from tgbot.filters.admin import AdminFilter
from tgbot.keyboards.inline.callback_factory import CancelingCallbackData

helpers_router = Router()


async def check_email(value):
    pattern = re.compile(r"^\S+@\S+\.\S+$")
    is_valid = pattern.match(value)
    if is_valid and len(value) < 250:
        return True


@helpers_router.callback_query(CancelingCallbackData.filter())
async def canceling(query: CallbackQuery, state: FSMContext):
    await state.clear()
    await query.message.edit_text(f"Отменено")
