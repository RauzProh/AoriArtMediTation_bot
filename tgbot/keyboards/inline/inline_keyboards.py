from aiogram.utils.keyboard import InlineKeyboardBuilder

from tgbot.keyboards.inline.callback_factory import CancelingCallbackData, SubscriptionCallbackData


async def canceling():
    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text=f"Отмена",
        callback_data=CancelingCallbackData(key="canceling")
    )
    keyboard.adjust(1, 1)
    return keyboard.as_markup()


async def subscription(url=False):
    keyboard = InlineKeyboardBuilder()
    if url:
        if type(url) == list:
            keyboard.button(
                text=f"Оплатить 599 ₽",
                url=str(url[0])
            )
            keyboard.button(
                text=f"🎁 Приобрести в подарок за 599 ₽",
                url=str(url[1])
            )
            keyboard.button(
                text="Написать мне, если сложности с оплатой в ₽",
                url="https://t.me/elena_mezrina"
            )
        else:
            keyboard.button(
                text=f"Оплатить 599 ₽",
                url=str(url)
            )
            keyboard.button(
                text="Написать мне, если сложности с оплатой в ₽",
                url="https://t.me/elena_mezrina"
            )

    else:
        keyboard.button(
            text=f"Купить в подарок",
            callback_data=SubscriptionCallbackData(key="update_email")
        )
        keyboard.button(
            text=f"Изменить email",
            callback_data=SubscriptionCallbackData(key="update_email")
        )
    keyboard.adjust(1, 1)
    return keyboard.as_markup()


async def before_buying(url):
    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text=f"🎁 Приобрести в подарок за 599 ₽",
        # callback_data="buy_as_a_gift_2"
        url=url
    )
    keyboard.button(
        text=f"Изменить email",
        callback_data=SubscriptionCallbackData(key="update_email")
    )
    keyboard.adjust(1, 1)
    return keyboard.as_markup()


async def add_mail():
    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text=f"Добавить email",
        callback_data=SubscriptionCallbackData(key="update_email")
    )
    keyboard.adjust(1, 1)
    return keyboard.as_markup()
