from aiogram.utils.keyboard import InlineKeyboardBuilder
from tgbot.keyboards.inline.callback_factory import ScenarioCallbackData_update

# Шаг 1: Приветствие
async def welcome_step():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Да", callback_data=ScenarioCallbackData_update(key="yes"))
    keyboard.button(text="Расскажи подробнее", callback_data=ScenarioCallbackData_update(key="more_info"))
    keyboard.button(text="Напомните позже", callback_data=ScenarioCallbackData_update(key="remind_later"))
    keyboard.adjust(1, 1)
    return keyboard.as_markup()

async def reminder_start_btn():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Начнем", callback_data=ScenarioCallbackData_update(key="yes"))
    keyboard.adjust(1, 1)
    return keyboard.as_markup()

#more_info
async def more_info():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Хорошо, начнем", callback_data=ScenarioCallbackData_update(key="yes"))
    keyboard.button(text="Напомните мне позже", callback_data=ScenarioCallbackData_update(key="remind_later"))
    keyboard.adjust(1, 1)
    return keyboard.as_markup()

# Шаг 2: Ввод e-mail
async def email_step():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Напомните мне позже", callback_data=ScenarioCallbackData_update(key="remind_email"))
    keyboard.adjust(1, 1)
    return keyboard.as_markup()

# Шаг 3: Выбор аудио-трека
async def audio_choice_step(selected=[]):
    keyboard = InlineKeyboardBuilder()
    if "leonardo" not in selected:
        keyboard.button(text="Расширить горизонты с Леонардо", callback_data=ScenarioCallbackData_update(key="audio_leonardo"))
    if "raphael" not in selected:
        keyboard.button(text="Ощутить опоры с Рафаэлем", callback_data=ScenarioCallbackData_update(key="audio_raphael"))
    if "durer" not in selected:
        keyboard.button(text="Ясно увидеть себя с Дюрером", callback_data=ScenarioCallbackData_update(key="audio_durer"))
    keyboard.adjust(1, 1)
    return keyboard.as_markup()


async def audio_choice_without(selected):
    keyboard = InlineKeyboardBuilder()
    if "leonardo" not in selected:
        keyboard.button(text="Расширить горизонты с Леонардо", callback_data=ScenarioCallbackData_update(key="audio_leonardo"))
    if "raphael" not in selected:
        keyboard.button(text="Ощутить опоры с Рафаэлем", callback_data=ScenarioCallbackData_update(key="audio_raphael"))
    if "durer" not in selected:
        keyboard.button(text="Ясно увидеть себя с Дюрером", callback_data=ScenarioCallbackData_update(key="audio_durer"))
    keyboard.adjust(1, 1)
    return keyboard.as_markup()

async def audio_choice_without2(selected):
    keyboard = InlineKeyboardBuilder()
    if "leonardo" not in selected[0] and "leonardo" not in selected[1]:
        keyboard.button(text="Да", callback_data=ScenarioCallbackData_update(key="yes"))
    if "raphael" not in selected and "raphael" not in selected[1]:
        keyboard.button(text="Да", callback_data=ScenarioCallbackData_update(key="yes"))
    if "durer" not in selected and "durer" not in selected[1]:
        keyboard.button(text="Да", callback_data=ScenarioCallbackData_update(key="yes"))
    keyboard.adjust(1, 1)
    return keyboard.as_markup()


async def finish_contin():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Продолжить", callback_data=ScenarioCallbackData_update(key="finish"))
    keyboard.adjust(1, 1)
    return keyboard.as_markup()

async def finishyes():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Кажется, да", callback_data=ScenarioCallbackData_update(key="yes"))
    keyboard.adjust(1, 1)
    return keyboard.as_markup()

# Шаг 4: Продолжить после аудио
async def continue_step():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Продолжить", callback_data=ScenarioCallbackData_update(key="continue"))
    keyboard.adjust(1, 1)
    return keyboard.as_markup()
    

async def continue_now():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Теперь дальше", callback_data=ScenarioCallbackData_update(key="continuenow"))
    keyboard.adjust(1, 1)
    return keyboard.as_markup()

# Шаг 5: Выбор дальнейшего пути
async def next_action_step():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Да, хочу продолжить опыт", callback_data=ScenarioCallbackData_update(key="continue_experience"))
    keyboard.button(text="Хочу индивидуальную сессию", callback_data=ScenarioCallbackData_update(key="private_session"))
    keyboard.button(text="Хочу поделиться впечатлениями", callback_data=ScenarioCallbackData_update(key="share_feedback"))
    keyboard.button(text="Подписаться на канал автора", callback_data=ScenarioCallbackData_update(key="subscribe_channel"))
    keyboard.button(text="Пока не слушал(а), напомни позже", callback_data=ScenarioCallbackData_update(key="remind_later_experience"))
    keyboard.adjust(1, 1)
    return keyboard.as_markup()

async def after_feedback():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Да, хочу продолжить опыт", callback_data=ScenarioCallbackData_update(key="continue_experience"))
    keyboard.button(text="Хочу индивидуальную сессию", callback_data=ScenarioCallbackData_update(key="private_session"))
    keyboard.button(text="Подписаться на канал автора", callback_data=ScenarioCallbackData_update(key="subscribe_channel"))

    keyboard.adjust(1, 1)
    return keyboard.as_markup()


async def finish():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Хочу индивидуальную сессию", callback_data=ScenarioCallbackData_update(key="private_session"))
    keyboard.button(text="Хочу поделиться впечатлениями", callback_data=ScenarioCallbackData_update(key="share_feedback"))
    keyboard.button(text="оплатить доступ в подарок", callback_data=ScenarioCallbackData_update(key="subscribe_channel"))
    keyboard.adjust(1, 1)
    return keyboard.as_markup()

# Шаг 6: Оплата / промокод
async def purchase_step():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Оплатить доступ за 1199 руб", callback_data=ScenarioCallbackData_update(key="buy"))
    keyboard.button(text="Купить доступ в подарок", callback_data=ScenarioCallbackData_update(key="gift"))
    keyboard.button(text="У меня есть промокод", callback_data=ScenarioCallbackData_update(key="promocode"))
    keyboard.button(text="Написать автору при сложностях с оплатой", url="https://t.me/elena_mezrina")
    keyboard.adjust(1, 1)
    return keyboard.as_markup()

async def check_pay_buttons(pay_id):
    print("Генерация кнопок")
    print(pay_id)
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Оплатить", url=pay_id[1])
    keyboard.button(text="Проверить оплату", callback_data=ScenarioCallbackData_update(key="oplata"))
    keyboard.adjust(1, 1)
    return keyboard.as_markup()

async def check_pay_buttons2(pay_id):
    print("Генерация кнопок")
    print(pay_id)
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Оплатить", url=pay_id[1])
    keyboard.button(text="Проверить оплату", callback_data=ScenarioCallbackData_update(key="oplata2"))
    keyboard.adjust(1, 1)
    return keyboard.as_markup()


async def purchase_step_1(link):
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Cсылка на оплату", url=link)
    keyboard.button(text="Купить доступ в подарок", callback_data=ScenarioCallbackData_update(key="gift"))
    keyboard.button(text="У меня есть промокод", callback_data=ScenarioCallbackData_update(key="promocode"))
    keyboard.button(text="Написать автору при сложностях с оплатой", url="https://t.me/elena_mezrina")
    keyboard.adjust(1, 1)
    return keyboard.as_markup()







# Шаг 7: Пост-продажа — выбор художника после покупки
async def post_purchase_choice(selected=[]):
    keyboard = InlineKeyboardBuilder()
    if "leonardo" not in selected:
        keyboard.button(text="Леонардо да Винчи", callback_data=ScenarioCallbackData_update(key="post_leonardo"))
    if "raphael" not in selected:
        keyboard.button(text="Рафаэль Санти", callback_data=ScenarioCallbackData_update(key="post_raphael"))
    if "durer" not in selected:
        keyboard.button(text="Альбрехт Дюрер", callback_data=ScenarioCallbackData_update(key="post_durer"))
    keyboard.adjust(1, 1)
    return keyboard.as_markup()

# Шаг 8: Завершение опыта
async def final_step():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Хочу индивидуальную сессию", callback_data=ScenarioCallbackData_update(key="final_session"))
    keyboard.button(text="Подписаться на канал автора", callback_data=ScenarioCallbackData_update(key="final_subscribe"))
    keyboard.button(text="Оплатить доступ в подарок", callback_data=ScenarioCallbackData_update(key="final_gift"))
    keyboard.adjust(1, 1)
    return keyboard.as_markup()

# Шаг 9: Оффлайн-событие
async def offline_event_step():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Купить билет за 4900 руб", callback_data=ScenarioCallbackData_update(key="ticket_buy"))
    keyboard.button(text="Расскажи подробнее", callback_data=ScenarioCallbackData_update(key="ticket_info"))
    keyboard.button(text="Напомни позже", callback_data=ScenarioCallbackData_update(key="ticket_remind"))
    keyboard.adjust(1, 1)
    return keyboard.as_markup()


async def offline_event_more():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Купить билет за 4900 руб", callback_data=ScenarioCallbackData_update(key="ticket_buy"))
    keyboard.button(text="Узнать больше", callback_data=ScenarioCallbackData_update(key="ticket_info_more"))
   
    keyboard.adjust(1, 1)
    return keyboard.as_markup()