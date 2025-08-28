import asyncio
from datetime import datetime
from aiogram import Router, F, types
from aiogram.filters import CommandStart, StateFilter, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile

from database.PostgreSQL import DatabasePSQL
from tgbot.keyboards.inline import scenario_uodate
from tgbot.keyboards.inline.callback_factory import ScenarioCallbackData_update
from tgbot.keyboards.default import reply_keyboards
from tgbot.misc.states import Scenario
from tgbot.misc.utils import remove_message, set_delayed_message
from tgbot.misc.payments import create_payment, check_oplata

scenario_router = Router()


@scenario_router.message(CommandStart())
async def start_scenario(message: Message, db_session: DatabasePSQL, state: FSMContext, config, command: CommandObject):
    await state.clear()
    
    print("/start")
    await db_session.add_user(full_name=message.from_user.full_name,
                              telegram_id=message.from_user.id,
                              username=message.from_user.username)

    text = ("Здравствуйте! Я автор. Как и вы. Автор решений, впечатлений, событий.\n\n"
            "Сегодня я приглашаю вас в особенное путешествие. Вы увидите знаменитый шедевр "
            "Возрождения своим внутренним зрением. Расширите свой личный горизонт, ощутите точки "
            "опоры на линии своей жизни, а, может, найдете ответы на свои вопросы. А я проведу вас "
            "голосом.\n\n"
            "Вам нужны 15 минут и наушники. Начнем?")

    await message.answer(text, reply_markup=await scenario_uodate.welcome_step())
    await db_session.add_reminder(message.from_user.id, 'start', 60*15)
    await db_session.add_reminder(message.from_user.id, 'start24', 60*30)


# Шаг 1 - сбор e-mail
@scenario_router.callback_query(ScenarioCallbackData_update.filter(F.key == "yes"), StateFilter(None))
async def step_1_email(query: types.CallbackQuery, state: FSMContext, db_session: DatabasePSQL):
    await query.bot.answer_callback_query(query.id)
    await db_session.cancel_reminder(query.from_user.id, 'start')
    await db_session.cancel_reminder(query.from_user.id, 'start24')
    await remove_message(query.message.delete_reply_markup)
    await query.message.answer(
        "Чтобы я могла прислать вам подарок, оставьте, пожалуйста, свой e-mail. "
        "Никакого спама, только избранные возможности для глубокого зрительского опыта."
    )
    await state.set_state(Scenario.get_email)

    await db_session.add_reminder(query.from_user.id, "email", 15)
    await db_session.add_reminder(query.from_user.id, "email24", 30)

    # # Напоминалки
    # set_delayed_message(chat_id=query.message.chat.id, delay=180,
    #                     text="Я буду рада выслать вам аудио-погружение сразу, как только вы напишете свой e-mail",
    #                     bot=query.bot, state=state, state_check=Scenario.get_email)

    # set_delayed_message(chat_id=query.message.chat.id, delay=86400,
    #                     text="Возможность на бесплатное аудио-погружение все еще доступна!",
    #                     bot=query.bot, state=state, state_check=Scenario.get_email)


@scenario_router.callback_query(ScenarioCallbackData_update.filter(F.key == "more_info"), StateFilter(None))
async def step_1_email(query: types.CallbackQuery, state: FSMContext):
    await query.bot.answer_callback_query(query.id)
    await query.message.answer("Это бесплатное аудио-погружение к своим ответам на важные\
вопросы. Свой вопрос можно сформулировать заранее или посмотреть, куда приведет вас\
дорога\n\n\
Вы смотрите на великую картину, слушаете мой голос и - видите\n\n\
15-20 минут вашего внимания. Часто этого достаточно, чтобы внутри проявилось то, что\
было скрыто", reply_markup=await scenario_uodate.more_info())

@scenario_router.message(Scenario.get_email)
async def get_email(message: Message, db_session: DatabasePSQL, state: FSMContext):
    email = message.text
    print(f'почта: {email}')
    if "@" in email and "." in email:
        print("Заходим почта")
        await state.clear()
        await db_session.update_mail_user(email, message.from_user.id)
        try:
            await db_session.cancel_reminder(message.from_user.id, 'email')
            await db_session.cancel_reminder(message.from_user.id, 'email24')
        except Exception as e:
            print(f"Ошибка: {e}")

        await message.answer(f"Чудесно! \n\nЧтобы нам не мешала дистанция, я позволю себе перейти на “ты”")
        await message.answer("Погружение в картину часто позволяет проявиться скрытому. Если ты хочешь поискать\
ответы на свой вопрос, сейчас самое время его сформулировать. Или позволь картине\
натолкнуть тебя на вопросы")
        await message.answer("Устраивайся поудобнее, надевай наушники и - выбирай направление сегодняшнего пути",
                             reply_markup=await scenario_uodate.audio_choice_step())
        await state.set_state(Scenario.before_audio)
        await db_session.add_reminder(message.from_user.id, 'choice_audio', 15)
        await db_session.add_reminder(message.from_user.id, 'choice_audio24', 30)
    else:
        await message.answer("Похоже, e-mail написан с ошибкой. Пожалуйста, отправь исправленный вариант.")


@scenario_router.callback_query(ScenarioCallbackData_update.filter(F.key.in_({"audio_leonardo", "audio_raphael", "audio_durer"})), StateFilter(Scenario.before_audio))
async def after_audio_step(query: types.CallbackQuery, state: FSMContext, db_session: DatabasePSQL):
    await query.bot.answer_callback_query(query.id)
    # check = await db_session.get_accesses(query.from_user.id)
    # print('check print')
    # print(check)
    # #Удалить
    # check = False
    # if check:
    #     data = await state.get_data()
    #     print(data)
    #     if data.get("second_audio_choice"):
    #         print('second data')
    #         print(data)
            
    #     else:
    #         key = query.data
    #         await state.update_data(second_audio_choice = key)
    #         audio_file = ''
    #         image_file = ''
    #         if "audio_leonardo" in key:
    #             print("Лео")
    #             audio_file = "Да Винчи.mp3"
    #             image_file = "Да Винчи.jpg"
    #         elif "audio_raphael" in key:
    #             audio_file = "Рафаель.mp3"
    #             image_file = "Рафаель.jpg"
    #         else:
    #             audio_file = "Дюрер.mp3"
    #             image_file = "Дюрер.jpg"
    #         print(audio_file)
    #         await query.message.answer_photo(FSInputFile(f"media/{image_file}"))
    #         await query.message.answer_audio(FSInputFile(f"media/{audio_file}"),
    #                                         reply_markup=await scenario_uodate.continue_step())

    # else:
    await db_session.cancel_reminder(query.from_user.id, 'choice_audio')
    await db_session.cancel_reminder(query.from_user.id, 'choice_audio24')
    await state.update_data(audio_choice=query.data)
    await state.set_state(Scenario.audio_choice)
    await query.message.answer_audio(FSInputFile(f"media/Настройся.mp3"),
                                    reply_markup=await scenario_uodate.continue_step())
    await db_session.add_reminder(query.from_user.id, 'first_audio', 15)

# Выбор аудио
@scenario_router.callback_query(ScenarioCallbackData_update.filter(F.key == "continue" ), StateFilter(Scenario.audio_choice))
async def send_audio_and_image(query: types.CallbackQuery, state: FSMContext, config, db_session: DatabasePSQL):
    await db_session.cancel_reminder(query.from_user.id, 'first_audio')
    await query.bot.answer_callback_query(query.id)
    await remove_message(query.message.delete_reply_markup)
    key = await state.get_data()
    print(key)
    key = key.get("audio_choice")
    print(key)
    audio_file = ''
    image_file = ''
    if "audio_leonardo" in key:
        print("Лео")
        audio_file = "Да Винчи.mp3"
        image_file = "Да Винчи.jpg"
    elif "audio_raphael" in key:
        audio_file = "Рафаель.mp3"
        image_file = "Рафаель.jpg"
    else:
        audio_file = "Дюрер.mp3"
        image_file = "Дюрер.jpg"
    print(audio_file)
    await query.message.answer_photo(FSInputFile(f"media/{image_file}"))
    await query.message.answer_audio(FSInputFile(f"media/{audio_file}"),
                                     reply_markup=await scenario_uodate.continue_step())
    # await db_session.add_reminder(query.from_user.id, 'after_audio', 3)
    # await db_session.add_reminder(query.from_user.id, 'after_audio3', 3)
    # await db_session.add_reminder(query.from_user.id, 'after_audio24', 3)




    await state.set_state(Scenario.after_audio)
    print('awdadwa')


@scenario_router.callback_query(ScenarioCallbackData_update.filter(F.key.in_({"audio_leonardo", "audio_raphael", "audio_durer"})), StateFilter(Scenario.post_audio_choice))
async def after_audio_step(query: types.CallbackQuery, state: FSMContext, db_session: DatabasePSQL):
    await query.bot.answer_callback_query(query.id)
    await db_session.cancel_reminder(query.from_user.id, "after_pay")
    check = await db_session.get_accesses(query.from_user.id)
    print('check print')
    print(check)
    #Удалить
    # check = False
    if check:
        data = await state.get_data()
        print(data)
        if data.get("second_audio_choice"):
            print('second data')
            print(data)
            
        else:
            key = query.data
            await state.update_data(second_audio_choice = key)
            audio_file = ''
            image_file = ''
            if "audio_leonardo" in key:
                print("Лео")
                audio_file = "Да Винчи.mp3"
                image_file = "Да Винчи.jpg"
            elif "audio_raphael" in key:
                audio_file = "Рафаель.mp3"
                image_file = "Рафаель.jpg"
            else:
                audio_file = "Дюрер.mp3"
                image_file = "Дюрер.jpg"
            print(audio_file)
            await query.message.answer_photo(FSInputFile(f"media/{image_file}"))
            await query.message.answer_audio(FSInputFile(f"media/{audio_file}"),
                                            reply_markup=await scenario_uodate.continue_step())
            await db_session.add_reminder(query.from_user.id, "after_pay", 60*30)

@scenario_router.callback_query(ScenarioCallbackData_update.filter(F.key == "continue" ), StateFilter(Scenario.post_audio_choice))
async def send_audio_and_image2(query: types.CallbackQuery, state: FSMContext, config, db_session: DatabasePSQL):
    await query.bot.answer_callback_query(query.id)
    await db_session.cancel_reminder(query.from_user.id, 'after_pay')
    data = await state.get_data()
    print(data)
    await db_session.add_reminder(query.from_user.id, "choice_audio_reminder", 60*30)
    await query.message.answer("Не торопись, дай себе время прочувствовать свой опыт до конца", reply_markup=await scenario_uodate.continue_now())
    await db_session.add_reminder(query.from_user.id, "after_pay", 60*30)


@scenario_router.callback_query(ScenarioCallbackData_update.filter(F.key == "continuenow" ), StateFilter(Scenario.post_audio_choice))
async def send_audio_and_image2(query: types.CallbackQuery, state: FSMContext, config, db_session: DatabasePSQL):
    await query.bot.answer_callback_query(query.id)
    await db_session.cancel_reminder(query.from_user.id, "choice_audio_reminder")
    await db_session.cancel_reminder(query.from_user.id, 'after_pay')
    data = await state.get_data()
    audio_choice = data['audio_choice']
    second_audio_choice = data ['second_audio_choice']
    selected = [audio_choice, second_audio_choice]
    audio_file = ''
    image_file = ''
    if "leonardo" not in selected[0] and "leonardo" not in selected[1]:
        audio_file = "Да Винчи.mp3"
        image_file = "Да Винчи.jpg"
    if "raphael" not in selected and "raphael" not in selected[1]:
        audio_file = "Рафаель.mp3"
        image_file = "Рафаель.jpg"
    if "durer" not in selected and "durer" not in selected[1]:
        audio_file = "Дюрер.mp3"
        image_file = "Дюрер.jpg" 
    await query.message.answer_photo(FSInputFile(f"media/{image_file}"))
    await query.message.answer_audio(FSInputFile(f"media/{audio_file}"),
                                            reply_markup=await scenario_uodate.continue_step())
    await state.set_state(Scenario.finish)
    await db_session.add_reminder(query.from_user.id, "after_pay", 60*30)
    


@scenario_router.callback_query(ScenarioCallbackData_update.filter(F.key == "finish"), StateFilter(Scenario.finish))
async def after_audio_step(query: types.CallbackQuery, state: FSMContext, db_session: DatabasePSQL):
    await query.bot.answer_callback_query(query.id)
    await db_session.cancel_reminder(query.from_user.id, 'after_pay')
    await query.message.answer('“Ну что же, кажется, пора завершать?', reply_markup=await scenario_uodate.finishyes())
    await db_session.add_reminder(query.from_user.id, "after_pay", 60*30)



@scenario_router.callback_query(ScenarioCallbackData_update.filter(F.key == "yes"), StateFilter(Scenario.finish))
async def after_audio_step(query: types.CallbackQuery, state: FSMContext, db_session: DatabasePSQL):
    await query.bot.answer_callback_query(query.id)
    await db_session.cancel_reminder(query.from_user.id, 'after_pay')
    audio_file = "В завершение.mp3"
    await query.message.answer_audio(FSInputFile(f"media/{audio_file}"),
                                            reply_markup=await scenario_uodate.continue_step())
    await db_session.add_reminder(query.from_user.id, "after_pay", 60*30)
    
    
@scenario_router.callback_query(ScenarioCallbackData_update.filter(F.key == "continue"), StateFilter(Scenario.finish))
async def after_audio_step(query: types.CallbackQuery, state: FSMContext):
    await query.bot.answer_callback_query(query.id)
    await query.message.answer("Я благодарю тебя за доверие и позволение этому опыту случиться.\n\n\
Для меня будет высшим признанием, если ты захочешь подарить доступ кому-то из друзей\
и остаться со мной на связи.\n\n\
А я желаю тебе свободы творчества и мечты. И прощаюсь",reply_markup= await scenario_uodate.finish())




@scenario_router.callback_query(ScenarioCallbackData_update.filter(F.key == "continue"), StateFilter(Scenario.after_audio))
async def after_audio_step(query: types.CallbackQuery, state: FSMContext, db_session: DatabasePSQL):
    await query.bot.answer_callback_query(query.id)
    print('Аудио продолжить')
    await remove_message(query.message.delete_reply_markup)
    await query.message.answer("Тебе понравилась дорога в свою глубину?",
                               reply_markup=await scenario_uodate.next_action_step())
    await state.set_state(Scenario.after_audio_options)
    try:
        await db_session.add_reminder(query.from_user.id, "firstpay", 60*30)
    except Exception as e:
            print(f"Ошибка: {e}")

# Ветви после выбора опций
@scenario_router.callback_query(ScenarioCallbackData_update.filter(F.key == "continue_experience"), StateFilter(Scenario.after_audio_options))
async def branch_continue(query: types.CallbackQuery, state: FSMContext, db_session: DatabasePSQL):
    await query.bot.answer_callback_query(query.id)
    await db_session.cancel_reminder(query.from_user.id, 'firstpay')
    await query.message.answer("Я рада идти вместе дальше. Оплачивай доступ или вводи промокод.",
                               reply_markup=await scenario_uodate.purchase_step())
    await state.set_state(Scenario.payment)


@scenario_router.callback_query(ScenarioCallbackData_update.filter(F.key == "share_feedback"), StateFilter(Scenario.after_audio_options))
async def branch_continue(query: types.CallbackQuery, state: FSMContext, db_session: DatabasePSQL):
    await query.bot.answer_callback_query(query.id)
    await db_session.cancel_reminder(query.from_user.id, 'start')
    await query.message.answer("Хочешь поделиться, что с тобой произошло?\
Напиши свой отзыв текстом — я внимательно всё прочитаю 💌")
    await state.set_state(Scenario.feedback)


@scenario_router.message(Scenario.feedback)
async def check_promo(message: Message, db_session: DatabasePSQL, state: FSMContext):
    await message.answer("Спасибо, это очень ценно 🙏\n\n\
Твои слова помогают делать этот путь глубже и живее.\n\n\
А теперь — куда идём дальше?", reply_markup = await scenario_uodate.after_feedback())
    await db_session.add_impression(message.from_user.id, message.text)
    await state.set_state(Scenario.after_audio_options)

# Оплата или промокод
@scenario_router.callback_query(ScenarioCallbackData_update.filter(F.key.in_({"buy", "gift", "promocode"})), StateFilter(Scenario.payment))
async def handle_payment(query: types.CallbackQuery, state: FSMContext, db_session: DatabasePSQL):
    await query.bot.answer_callback_query(query.id)
    await db_session.cancel_reminder(query.from_user.id, 'start')
    print(query.data)
    data = await state.get_data()
    print(data)
    user = await db_session.get_mail_user(query.from_user.id)
    mail = user['mail']
    if  "buy" in query.data:
        payment_url = await create_payment(amount=1199, email=mail, gift=False)
        print(payment_url)
        await state.update_data(payment_link=payment_url)
        # try:
        #     await query.message.edit_reply_markup(reply_markup=await scenario_uodate.purchase_step_1(payment_url[1]))
        # except:
        #     await query.message.answer('Оплата:', reply_markup=await scenario_uodate.purchase_step_1(payment_url[1]))
        await query.message.answer('Оплата:', reply_markup=await scenario_uodate.check_pay_buttons(payment_url))
    elif "gift" in query.data:
        payment_url = await create_payment(amount=1199, email=mail, gift=True)
        await query.message.answer(f"Ссылка для подарка: {payment_url}")
    elif "promocode" in query.data:
        await query.message.answer("Введите промокод:")
        await state.set_state(Scenario.enter_promo)

@scenario_router.callback_query(ScenarioCallbackData_update.filter(F.key == "oplata"), StateFilter(Scenario.payment))
async def checkoplaya(query: types.CallbackQuery, state: FSMContext, db_session: DatabasePSQL):
    await query.bot.answer_callback_query(query.id)
    data = await state.get_data()
    print(data)
    check = await check_oplata(data['payment_link'][0])
    choice_audio = data['audio_choice']

    #Удалить
    check = "succeeded"


    print(check)
    if check =="pending":
        await query.message.answer("Оплаты не было.")
    elif check == "succeeded":
        try:
            await db_session.add_accesses(query.from_user.id)
        except Exception as e:
            print(f"Ошибка: {e}")
        await query.message.answer("Теперь все готово. Выбирай, с кем\
из художников мы продолжим путь\
помни, что ты можешь идти со своим запросом", reply_markup=await scenario_uodate.audio_choice_without(choice_audio))
        await state.set_state(Scenario.post_audio_choice)
        await db_session.add_reminder(query.from_user.id, "after_pay", 60*30)
        


@scenario_router.message(Scenario.enter_promo)
async def check_promo(message: Message, db_session: DatabasePSQL, state: FSMContext):
    code = message.text

    valid = await db_session.get_promocode_by_code(code)
    data = await state.get_data()
    choice_audio = data['audio_choice']

    #убрать
    valid = True


    if valid:
        try:
            await db_session.add_accesses(message.from_user.id)
        except Exception as e:
            print(f"Ошибка: {e}")
        await message.answer("Теперь все готово. Выбирай, с кем\
из художников мы продолжим путь\
помни, что ты можешь идти со своим запросом", reply_markup=await scenario_uodate.audio_choice_without(choice_audio))
        await db_session.add_reminder(message.from_user.id, "after_pay", 60*30)
        await state.set_state(Scenario.post_audio_choice)
    else:
        await message.answer("Неверный промокод. Попробуй еще раз или оплати доступ.")


# Ветка оффлайн-события
@scenario_router.callback_query(ScenarioCallbackData_update.filter(F.key.in_({"ticket_buy", "ticket_info", "ticket_remind"})))
async def offline_event(query: types.CallbackQuery):
    await query.bot.answer_callback_query(query.id)
    if query.data == "ticket_buy":
        await query.message.answer("Ссылка для покупки билета 4900 руб: https://payment_link")
    elif query.data == "ticket_info":
        await query.message.answer("Описание оффлайн-события: камерное обсуждение шедевра, опыт глубины, контакт с искусством.")
    elif query.data == "ticket_remind":
        # пример отложенного пуша через 3 часа
        asyncio.create_task(asyncio.sleep(10800))
        await query.message.answer("Напоминание: оффлайн-событие скоро, не пропусти!")




@scenario_router.callback_query(ScenarioCallbackData_update.filter(F.key == "private_session"))
async def feedback_global_handler(query: types.CallbackQuery, state: FSMContext):
    await query.bot.answer_callback_query(query.id)
    print("Private")
    await query.answer()  # Убирает "часики" в телеге
    # Можно сменить state, если нужно
    # await state.set_state(Scenario.feedback)
    await query.message.answer("сессия с автором - ссылка на лэнд или тг-пост")