import re

from aiogram import Router, F, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from database.PostgreSQL import DatabasePSQL
from tgbot.keyboards.inline import inline_keyboards
from tgbot.keyboards.inline.callback_factory import SubscriptionCallbackData
from tgbot.misc.payments import create_payment
from tgbot.misc.states import Subscription
from tgbot.misc.utils import remove_message

access_router = Router()


@access_router.message(Subscription.email)
async def get_email(message: Message, db_session: DatabasePSQL, state: FSMContext, config):
    data = await state.get_data()
    await remove_message(message.bot.delete_message, chat_id=message.chat.id, message_id=data.get("message_id"))

    mail = message.text.strip()
    pattern = re.compile(r"^\S+@\S+\.\S+$")
    is_valid = pattern.match(mail)

    if is_valid and len(mail) < 250:
        await state.clear()
        await db_session.update_mail_user(mail, message.from_user.id)
        gift = True
        amount = config.tg_bot.price
        payment_id, link = await create_payment(amount, mail, gift)
        await db_session.create_payment(message.from_user.id, amount, gift, payment_id)

        return await message.answer(
            f"Отлично, новый email - {mail} принят\n\n"
            f"После оплаты сюда придёт ссылка, которую можно будет переслать другу.\n"
            f"Перейдя по ней, он сможет прожить свой опыт погружения в три великие картины\n\n",
            reply_markup=await inline_keyboards.before_buying(link))
    await message.answer(
        "Упс, похоже в вашем email допущена ошибка, проверьте правильность ввода и пришлите корректную версию",
        reply_markup=await inline_keyboards.canceling())


@access_router.callback_query(SubscriptionCallbackData.filter(F.key == "update_email"), StateFilter(None))
async def update_email(query: types.CallbackQuery, state: FSMContext):
    await state.set_state(Subscription.email)
    bot_message = await query.message.edit_text(
        "Для совершения покупок нужно указать email для отправки чека, пожалуйста отправьте его боту",
        reply_markup=await inline_keyboards.canceling())
    await state.update_data(message_id=bot_message.message_id)
    return bot_message
