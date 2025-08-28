import asyncio
from datetime import datetime
from typing import Union

from aiogram import Router, F, types
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart, StateFilter, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.middleware import FSMContextMiddleware
from aiogram.types import Message, FSInputFile

from database.PostgreSQL import DatabasePSQL
from tgbot.filters.admin import AdminFilter
from tgbot.handlers.helpers import check_email
from tgbot.keyboards.default import reply_keyboards
from tgbot.keyboards.inline import scenario_keyboards
from tgbot.keyboards.inline.callback_factory import ScenarioCallbackData
from tgbot.keyboards.inline.inline_keyboards import subscription
from tgbot.misc.payments import create_payment
from tgbot.misc.states import Scenario
from tgbot.misc.utils import remove_message

scenario_router = Router()


@scenario_router.message(CommandStart())
async def step_1(message: Message, db_session: DatabasePSQL, state: FSMContext, config, command: CommandObject):
    await state.clear()
    await db_session.add_user(full_name=message.from_user.full_name, telegram_id=message.from_user.id,
                              username=message.from_user.username)
    ticket = command.args

    if ticket:
        ticket = int(ticket)
        status_ticket = await db_session.get_ticket(ticket, message.from_user.id)
        if status_ticket:
            await db_session.update_ticket(ticket, message.from_user.id, datetime.now())
            await db_session.add_accesses(message.from_user.id)
    else:
        if await db_session.select_buyer_with_name_and_email(message.from_user.id):
            await message.answer("Теперь все готово. "
                                 "Устраивайся поудобнее, настраивайся на неспешный темп,"
                                 " включай аудио и следуй за моим голосом")
            audio = FSInputFile(config.misc.path_media + "Настройся.mp3")
            return await message.answer_audio(audio, reply_markup=await scenario_keyboards.step_7())

    await message.answer(text=f"Здравствуйте! Я автор. Как и вы. Автор решений, впечатлений, событий\n\n"
                              f"Сегодня я приглашаю вас в особенное путешествие. Вы увидите знаменитый шедевр\
Возрождения своим внутренним зрением. Расширите свой личный горизонт, ощутите точки\
опоры на линии своей жизни, а, может, найдете ответы на свои вопросы. А я проведу вас\
голосом.\n\n"
                              f"Вам нужны 15 минут и наушники \n\n"
                              f"Начнем?»")


@scenario_router.callback_query(ScenarioCallbackData.filter(F.key == "1"), StateFilter(None))
async def step_2(query: types.CallbackQuery, state: FSMContext):
    await remove_message(query.message.delete_reply_markup)
    await query.message.answer("Спасибо!\nСкажите, пожалуйста, как вас зовут?")
    await state.set_state(Scenario.get_name)


@scenario_router.message(Scenario.get_name)
async def step_3(message: Message, db_session: DatabasePSQL, state: FSMContext):
    if len(message.text) > 250:
        return await message.answer("Имя должно быть короче 250 символов, введите корректный вариант")
    await state.clear()
    await db_session.update_entered_name_user(message.text, message.from_user.id)
    await message.answer(f"Благодарю, {message.text}! Приятно познакомиться.\n"
                         "Пока вы тут осваиваетесь, я расскажу, как все будет происходить.")
    await asyncio.sleep(1)

    await message.answer(f"Вы смотрите на картину на своем экране, я вам ее пришлю, и слушаете мой голос.\n"
                         f"Мечтаете, рисуете, чувствуете, творите вслед за замыслом художника.")
    await asyncio.sleep(1)

    await message.answer(f"Я верю, что каждый зритель - соавтор картины. И вы тоже соавтор.\n"
                         f"Возможно, сегодня вы ощутите силу сотворчества.")
    await asyncio.sleep(1)

    await message.answer(f"В основе творчества или искусства близкий контакт и тонкое чувствование мира. "
                         f"Я хочу чуть-чуть к вам приблизиться, чтобы вдохновению было проще заполнить пространство. "
                         f"И прошу вашего позволения обращаться к вам на “ты”.",
                         reply_markup=await scenario_keyboards.step_3())


@scenario_router.callback_query(ScenarioCallbackData.filter(F.key == "3"), StateFilter(None))
async def step_4(query: types.CallbackQuery):
    await remove_message(query.message.delete_reply_markup)
    await query.message.answer("Чудесно.")
    await asyncio.sleep(1)
    await query.message.answer("Следующие 40-50 минут будут насыщенными.\n\n"
                               "Я мечтаю, чтобы они принесли тебе не только новую точку зрения на известные шедевры, "
                               "но и богатый внутренний опыт.")
    await asyncio.sleep(1)

    await query.message.answer(
        "Если ты тоже этого хочешь, пожалуйста, выбери себе место, где тебе будет удобно и никто нас не прервет.")
    await asyncio.sleep(1)

    await query.message.answer("Еще тебе понадобятся наушники, карандаш и лист бумаги. Возьми их.")
    await asyncio.sleep(1)

    await query.message.answer("Готово?", reply_markup=await scenario_keyboards.step_4())


@scenario_router.callback_query(ScenarioCallbackData.filter(F.key == "4"), StateFilter(None))
async def step_5(query: types.CallbackQuery, state: FSMContext, db_session: DatabasePSQL, config):
    await remove_message(query.message.delete_reply_markup)

    if await db_session.get_accesses(query.from_user.id):
        await query.message.answer("Теперь все готово. "
                                   "Устраивайся поудобнее, настраивайся на неспешный темп, включай аудио"
                                   " и следуй за моим голосом")
        audio = FSInputFile(config.misc.path_media + "Настройся.mp3")
        await query.message.answer_audio(audio, reply_markup=await scenario_keyboards.step_7())
        return

    await query.message.answer("Напиши, пожалуйста, твой e-mail\n\n"
                               "Я не люблю спам и не рассылаю его.\n"
                               "После оплаты билета на этот адрес придет чек.\n\n"
                               "Возможно, когда-нибудь я создам что-то еще для глубокого зрительского опыта, "
                               "и тогда поделюсь с тобой.")

    await state.set_state(Scenario.get_email)


@scenario_router.message(Scenario.get_email)
async def step_6(message: Message, db_session: DatabasePSQL, state: FSMContext):
    mail = message.text

    if await check_email(mail):
        await state.clear()
        name = (await db_session.select_user(telegram_id=message.from_user.id)).get("entered_name")
        await db_session.update_mail_user(mail, message.from_user.id)
        return await message.answer(f"Спасибо, {name}.\nОстался последний шаг.",
                                    reply_markup=await scenario_keyboards.step_6())
    await message.answer("Похоже e-mail написан с ошибкой, пожалуйста, отправь исправленный вариант")


@scenario_router.callback_query(ScenarioCallbackData.filter(F.key == "promocode"), StateFilter(None))
async def request_promocode(query: types.CallbackQuery, state: FSMContext):
    await query.answer(cache_time=15)
    await query.message.answer('Введи свой промокод')
    await state.set_state('get_promocode')


@scenario_router.message(StateFilter('get_promocode'))
async def get_promocode(message: types.Message, state: FSMContext, db_session: DatabasePSQL):
    code = message.text
    if await db_session.get_promocode_by_code(code):
        await db_session.update_promocode(code, message.from_user.id)
        await db_session.add_accesses(message.from_user.id)

        text = (f"Теперь все готово.\nУстраивайся поудобнее, настраивайся на неспешный темп, включай аудио"
                f" и следуй за моим голосом")
        await state.clear()
        await message.answer(text)
        audio = FSInputFile("media/Настройся.mp3")
        await message.answer_audio(audio=audio, reply_markup=await scenario_keyboards.step_7())
    else:
        await message.reply('Промокод не найден. Попробуй снова')


@scenario_router.callback_query(ScenarioCallbackData.filter(F.key == "buy_yourself"))
async def step_7(query: types.CallbackQuery, state: FSMContext, db_session: DatabasePSQL, config):
    await state.clear()
    mail = (await db_session.get_mail_user(query.from_user.id)).get("mail")
    amount = config.tg_bot.price
    payment_id, link = await create_payment(amount, mail, False)
    await db_session.create_payment(query.from_user.id, amount, False, payment_id)

    try:
        await query.message.edit_reply_markup(reply_markup=await subscription(link))
    except:
        await query.message.answer('Оплата:', reply_markup=await subscription(link))


@scenario_router.callback_query(F.data == 'buy_as_a_gift')
async def step_7(call: types.CallbackQuery, db_session: DatabasePSQL, state: FSMContext, config):
    await state.clear()
    mail = (await db_session.get_mail_user(call.from_user.id)).get("mail")
    amount = config.tg_bot.price
    payment_id1, link1 = await create_payment(amount, mail, False)
    await db_session.create_payment(call.from_user.id, amount, False, payment_id1)

    payment_id2, link2 = await create_payment(amount, mail, True)
    await db_session.create_payment(call.from_user.id, amount, True, payment_id2)

    try:
        await call.message.edit_reply_markup(reply_markup=await subscription([link1, link2]))
    except:
        await call.message.answer(f"Остался последний шаг.",
                                  reply_markup=await subscription([link1, link2]))


@scenario_router.callback_query(ScenarioCallbackData.filter(F.key == "7"), StateFilter(None))
async def step_8(query: types.CallbackQuery, state: FSMContext):
    await remove_message(query.message.delete_reply_markup)
    await state.update_data(lst=[])
    await query.message.answer("С каким художником ты хочешь творить сейчас?",
                               reply_markup=await scenario_keyboards.painters([]))
    await state.set_state(Scenario.painter_choice)


@scenario_router.callback_query(ScenarioCallbackData.filter(F.key.in_({"l", "r", "a"})),
                                StateFilter(Scenario.painter_choice))
async def step_9(query: types.CallbackQuery, db_session: DatabasePSQL, callback_data: ScenarioCallbackData,
                 state: FSMContext, config):
    await remove_message(query.message.delete_reply_markup)
    key = callback_data.key
    data = await state.get_data()
    lst = data.get("lst")
    lst.append(key)
    await state.update_data(lst=lst)

    if key == "l":
        image = "Да Винчи.jpg"
        audio = "Да Винчи.mp3"

    elif key == "a":
        image = "Дюрер.jpg"
        audio = "Дюрер.mp3"

    else:
        image = "Рафаель.jpg"
        audio = "Рафаель.mp3"

    photo = FSInputFile(config.misc.path_media + image)
    audio = FSInputFile(config.misc.path_media + audio)

    await query.message.answer_photo(photo)
    await query.message.answer_audio(audio, reply_markup=await scenario_keyboards.step_9())
    await state.set_state(Scenario.next)


@scenario_router.callback_query(ScenarioCallbackData.filter(F.key == "9"), StateFilter(Scenario.next))
async def step_9_1(query: types.CallbackQuery, db_session: DatabasePSQL, state: FSMContext):
    await remove_message(query.message.delete_reply_markup)
    data = await state.get_data()
    lst = data.get("lst")

    if len(lst) == 1:
        txt = "Не спеши переходить к следующему художнику. " \
              "Дай себя время прожить свои впечатления до конца и впустить внутрь осознания. " \
              "Ты можешь записать их в поле для сообщений, чтобы легко вернуться к ним после."
    elif len(lst) == 2:
        name = (await db_session.select_user(telegram_id=query.from_user.id)).get("entered_name")
        txt = (f"{name}, я верю, что твой мир сейчас становится глубже, а горизонт шире. Ты можешь просто наслаждаться"
               f" этим состоянием, или, если хочешь, запиши, что в нем самое важное. "
               f"В конце ты сможешь вернуться к этим записям.")
    else:
        txt = ("Самое ценное в любой встрече с искусством - твои чувства и лично твои открытия. В поле для сообщений"
               " можно записать все твои ощущения, воспоминания, вопросы, идеи, чтобы легко их вспомнить позже ")

    message_del = await query.message.answer(txt, reply_markup=await scenario_keyboards.step_9_1())
    await state.update_data(message_id=message_del.message_id)
    await state.set_state(Scenario.get_impressions)


@scenario_router.message(Scenario.get_impressions)
@scenario_router.callback_query(ScenarioCallbackData.filter(F.key == "9_1"), StateFilter(Scenario.get_impressions))
async def step_10(query: Union[types.Message, types.CallbackQuery], db_session: DatabasePSQL, state: FSMContext):
    data = await state.get_data()
    lst = data.get("lst")
    message_del = data.get("message_id")

    if len(lst) == 1:
        txt = "Когда почувствуешь, что пора двигаться дальше, выбирай, с кем ты хочешь это сделать"
        keyboard = await scenario_keyboards.painters(lst)
        await state.set_state(Scenario.painter_choice)
    elif len(lst) == 2:
        txt = "Когда почувствуешь, что пора, делай шаг"
        keyboard = await scenario_keyboards.painters(lst)
        await state.set_state(Scenario.painter_choice)
    else:
        name = (await db_session.select_user(telegram_id=query.from_user.id)).get("entered_name")
        txt = f"Ну что же, кажется, пора завершать, {name}?"
        keyboard = await scenario_keyboards.step_10()
        await state.clear()

    if isinstance(query, Message):
        if len(query.text) > 4000:
            return query.answer("Упс, слишком длинный текст, попробуйте сократить")
        await db_session.add_impression(query.from_user.id, query.text)

        await remove_message(query.bot.delete_message, chat_id=query.chat.id, message_id=message_del)
        await query.answer(txt, reply_markup=keyboard)

    else:
        await query.message.edit_text(txt, reply_markup=keyboard)


@scenario_router.callback_query(ScenarioCallbackData.filter(F.key == "10"), StateFilter(None))
async def step_11(query: types.CallbackQuery, config):
    await remove_message(query.message.delete_reply_markup)
    audio = FSInputFile(config.misc.path_media + "В завершение.mp3")
    await query.message.answer_audio(audio, reply_markup=await scenario_keyboards.step_11())


@scenario_router.callback_query(ScenarioCallbackData.filter(F.key == "11"), StateFilter(None))
async def step_12(query: types.CallbackQuery):
    await remove_message(query.message.delete_reply_markup)
    await query.message.answer(f"Магия встречи с искусством для меня в том, что это "
                               f"одновременно и встреча с собой.")
    await asyncio.sleep(1)
    await query.message.answer(f"Я надеюсь, сегодня встреча случилась. И буду рада, если для тебя она продолжится: "
                               f"твои заметки доступны из меню, ты можешь к ним вернуться в любой момент.",
                               reply_markup=await scenario_keyboards.step_12())


@scenario_router.callback_query(ScenarioCallbackData.filter(F.key == "12"), StateFilter(None))
async def step_13(query: types.CallbackQuery, db_session: DatabasePSQL):
    await remove_message(query.message.delete_reply_markup)
    name = (await db_session.select_user(telegram_id=query.from_user.id)).get("entered_name")
    await query.message.answer(
        f"{name}, я хочу поблагодарить тебя за твое доверие и позволение этому опыту случиться.\n"
        f"Для меня в этом много магии.\nСпасибо.")
    await asyncio.sleep(1)

    await query.message.answer(
        f"Мне будет ценно узнать о твоих впечатлениях напрямую или остаться на связи в моем канале.")
    await asyncio.sleep(1)

    await query.message.answer(
        f"А если ты захочешь подарить сегодняшний опыт кому-то из друзей, для меня это будет высшим признанием.")
    await asyncio.sleep(1)

    await query.message.answer(
        f"Все эти возможности есть в меню.",
        reply_markup=reply_keyboards.main_menu)
    await asyncio.sleep(1)

    await query.message.answer(
        f"Желаю тебе свободы творчества и мечты, {name}.\n"
        f"И прощаюсь")
