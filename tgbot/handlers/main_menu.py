import logging

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from database.PostgreSQL import DatabasePSQL
from tgbot.filters.buyer import BuyerFilter
from tgbot.keyboards.default import reply_keyboards
from tgbot.keyboards.inline import inline_keyboards
from tgbot.keyboards.inline.inline_keyboards import canceling
from tgbot.misc.payments import create_payment
from tgbot.misc.states import MainMenu, Subscription
from tgbot.misc.utils import remove_message

main_menu_router = Router()
main_menu_router.message.filter(BuyerFilter())


@main_menu_router.message(F.text == 'Купить доступ в подарок')
async def access_menu(message: Message, state: FSMContext, db_session: DatabasePSQL):
    await state.clear()
    mail = (await db_session.get_mail_user(message.from_user.id)).get("mail")
    if not mail:
        await message.answer("Напиши, пожалуйста, твой e-mail\n\n"
                                    "Я не люблю спам и не рассылаю его.\n"
                                    "После оплаты билета на этот адрес придет чек.\n\n"
                                    "Возможно, когда-нибудь я создам что-то еще для глубокого зрительского опыта, "
                                    "и тогда поделюсь с тобой.", reply_markup=await inline_keyboards.canceling())

        await state.set_state(Subscription.email)
        return
    gift = True
    amount = config.tg_bot.price
    payment_id, link = await create_payment(amount, mail, gift)
    await db_session.create_payment(message.from_user.id, amount, gift, payment_id)

    await message.answer(f"После оплаты сюда придёт ссылка, которую можно будет переслать другу.\n"
                         f"Перейдя по ней, он сможет прожить свой опыт погружения в три великие картины\n\n"
                         f"<i>{'Твой email для получения чека - ' + mail if mail else 'еще не был добавлен'}</i>",
                         reply_markup=await inline_keyboards.before_buying(link))


@main_menu_router.message(F.text == "Поделиться впечатлениями с автором")
async def share_your_impressions(message: Message, state: FSMContext):
    await state.clear()
    message_del = await message.answer("Напиши здесь свои впечатления и они будут переданы автору",
                                       reply_markup=await canceling())
    await state.update_data(message_id=message_del.message_id)
    await state.set_state(MainMenu.get_impressions)


@main_menu_router.message(F.text == "Перейти в канал автора")
async def share_your_impressions(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("https://t.me/elenamezrina")


@main_menu_router.message(F.text == "Взглянуть на свои открытия")
async def get_discoveries(message: Message, db_session: DatabasePSQL, state: FSMContext):
    await state.clear()

    impressions = await db_session.select_impression(user_id=message.from_user.id)
    for i in impressions:
        await message.answer(i.get("text"))


@main_menu_router.message(MainMenu.get_impressions)
async def get_impression(message: Message, db_session: DatabasePSQL, state: FSMContext):
    if len(message.text) > 4000:
        return message.answer("Упс, слишком длинный текст, попробуйте сократить")
    await db_session.add_impression(message.from_user.id, message.text)
    data = await state.get_data()

    try:
        await message.bot.send_message(-1002427177188, message.html_text)
    except:
        logging.exception('Канал')

    await remove_message(message.bot.delete_message, chat_id=message.from_user.id, message_id=data.get("message_id"))
    await message.answer("Спасибо!\nТвоё сообщение отправлено автору", reply_markup=reply_keyboards.main_menu)
    await state.clear()
