from aiogram.utils.keyboard import InlineKeyboardBuilder

from tgbot.keyboards.inline.callback_factory import ScenarioCallbackData


async def step_1():
    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text=f"Продолжайте",
        callback_data=ScenarioCallbackData(key="1")
    )
    keyboard.adjust(1, 1)
    return keyboard.as_markup()


async def step_3():
    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text=f"Хорошо",
        callback_data=ScenarioCallbackData(key="3")
    )
    keyboard.adjust(1, 1)
    return keyboard.as_markup()


async def step_4():
    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text=f"Готово",
        callback_data=ScenarioCallbackData(key="4")
    )
    keyboard.adjust(1, 1)
    return keyboard.as_markup()


async def step_6():
    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text=f"У меня есть промокод",
        callback_data=ScenarioCallbackData(key="promocode")
    )

    keyboard.button(
        text=f"Оплатить доступ за 599 рублей",
        callback_data=ScenarioCallbackData(key="buy_yourself")
    )
    keyboard.button(
        text=f"Оплатить доступ в подарок за 599 рублей",
        callback_data="buy_as_a_gift"
    )
    keyboard.button(
        text="Написать мне, если сложности с оплатой в ₽",
        url="https://t.me/elena_mezrina"
    )
    keyboard.adjust(1, 1)
    return keyboard.as_markup()


async def step_7():
    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text=f"Продолжить",
        callback_data=ScenarioCallbackData(key="7"))
    keyboard.adjust(1, 1)
    return keyboard.as_markup()


async def painters(lst):
    keyboard = InlineKeyboardBuilder()
    if "l" not in lst:
        keyboard.button(
            text=f"Леонардо да Винчи",
            callback_data=ScenarioCallbackData(key="l"))
    if "r" not in lst:
        keyboard.button(
            text=f"Рафаэль Санти",
            callback_data=ScenarioCallbackData(key="r"))
    if "a" not in lst:
        keyboard.button(
            text=f"Альбрехт Дюрер",
            callback_data=ScenarioCallbackData(key="a"))
    keyboard.adjust(1, 1)
    return keyboard.as_markup()


async def step_9():
    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text=f"Продолжить",
        callback_data=ScenarioCallbackData(key="9"))
    keyboard.adjust(1, 1)
    return keyboard.as_markup()


async def step_9_1():
    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text=f"Пропустить",
        callback_data=ScenarioCallbackData(key="9_1"))
    keyboard.adjust(1, 1)
    return keyboard.as_markup()


async def step_10():
    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text=f"Кажется, да",
        callback_data=ScenarioCallbackData(key="10"))
    keyboard.adjust(1, 1)
    return keyboard.as_markup()


async def step_11():
    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text=f"Продолжить",
        callback_data=ScenarioCallbackData(key="11"))
    keyboard.adjust(1, 1)
    return keyboard.as_markup()


async def step_12():
    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text=f"Продолжить",
        callback_data=ScenarioCallbackData(key="12"))
    keyboard.adjust(1, 1)
    return keyboard.as_markup()