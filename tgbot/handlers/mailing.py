import logging
from aiogram import Router, F, types
from aiogram.filters import StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from core.bot import bot
from database.PostgreSQL import DatabasePSQL

router = Router()


# ---------------------- FSM STATES ----------------------
class BroadcastStates(StatesGroup):
    waiting_for_text = State()
    waiting_for_photo = State()
    waiting_for_format = State()
    waiting_for_buttons = State()
    preview = State()  # предпросмотр


# ---------------------- INLINE KEYBOARDS ----------------------
def format_selection_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Markdown", callback_data="set_mode:Markdown")],
        [InlineKeyboardButton(text="HTML", callback_data="set_mode:HTML")],
        [InlineKeyboardButton(text="Нет", callback_data="set_mode:None")],
    ])


def confirm_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Подтвердить", callback_data="confirm_send")],
        [InlineKeyboardButton(text="Отмена", callback_data="cancel")],
    ])


def build_keyboard(buttons_data: list[dict]) -> InlineKeyboardMarkup | None:
    """
    Конвертирует список словарей {'text': ..., 'url': ...} в InlineKeyboardMarkup
    """
    if not buttons_data:
        return None
    keyboard = [[InlineKeyboardButton(text=btn["text"], url=btn["url"])] for btn in buttons_data]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# ---------------------- START BROADCAST ----------------------
@router.message(Command("broadcast"))
async def start_broadcast(message: Message, state: FSMContext):
    await state.set_state(BroadcastStates.waiting_for_text)
    await message.answer("Отправьте текст для рассылки:")


# ---------------------- HANDLE TEXT ----------------------
@router.message(BroadcastStates.waiting_for_text, F.content_type == "text")
async def handle_text(message: Message, state: FSMContext):
    await state.update_data(text=message.text)
    await state.set_state(BroadcastStates.waiting_for_photo)
    await message.answer("Теперь отправьте фотографию для рассылки:")


# ---------------------- HANDLE PHOTO ----------------------
@router.message(BroadcastStates.waiting_for_photo, F.content_type == "photo")
async def handle_photo(message: Message, state: FSMContext):
    await state.update_data(photo_id=message.photo[-1].file_id)
    await state.set_state(BroadcastStates.waiting_for_format)
    await message.answer("Выберите форматирование текста:", reply_markup=format_selection_keyboard())


# ---------------------- SET FORMAT ----------------------
@router.callback_query(F.data.startswith("set_mode:"), StateFilter(BroadcastStates.waiting_for_format))
async def set_format(callback: types.CallbackQuery, state: FSMContext):
    mode = callback.data.split(":")[1]
    await state.update_data(parse_mode=None if mode == "None" else mode)
    await state.set_state(BroadcastStates.waiting_for_buttons)
    await callback.message.answer(
        "Пришлите кнопки с ссылками в формате:\nТекст - URL (по одному в строке, каждое на новой строке)"
    )



# ---------------------- HANDLE BUTTONS ----------------------
@router.message(BroadcastStates.waiting_for_buttons, F.content_type == "text")
async def handle_buttons(message: Message, state: FSMContext):
    buttons_data = []
    for row in message.text.split("\n"):
        if "-" not in row:  # пропускаем некорректные строки
            continue
        text, url = map(str.strip, row.split("-", 1))
        buttons_data.append({"text": text, "url": url})

    if not buttons_data:
        await message.answer("Ошибка: не удалось разобрать кнопки. Формат: Текст - URL")
        return

    await state.update_data(keyboard=buttons_data)
    await state.set_state(BroadcastStates.preview)

    # отправляем предпросмотр
    data = await state.get_data()
    preview_markup = build_keyboard(buttons_data)
    await message.answer_photo(
        photo=data["photo_id"],
        caption=data["text"],
        parse_mode=data.get("parse_mode"),
        reply_markup=preview_markup
    )

    # отдельное сообщение для подтверждения
    await message.answer(
        "Отправлять рассылку?",
        reply_markup=confirm_keyboard()
    )


# ---------------------- CONFIRM AND SEND ----------------------
@router.callback_query(F.data == "confirm_send", StateFilter(BroadcastStates.preview))
async def confirm_send(callback: types.CallbackQuery, db_session: DatabasePSQL, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    text = data["text"]
    photo_id = data["photo_id"]
    parse_mode = data.get("parse_mode")
    keyboard_data = data.get("keyboard")

    user_ids = await db_session.select_all_users()

    for user in user_ids:
        try:
            await callback.bot.send_photo(
                chat_id=user["telegram_id"],
                photo=photo_id,
                caption=text,
                parse_mode=parse_mode,
                reply_markup=build_keyboard(keyboard_data)
            )
        except Exception as e:
            logging.error(f"Ошибка при отправке пользователю {user}: {e}")

    await callback.message.answer("Рассылка завершена!")
    await state.clear()


# ---------------------- CANCEL ----------------------
@router.callback_query(F.data == "cancel")
async def cancel_action(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("Рассылка отменена.")
    await state.clear()
