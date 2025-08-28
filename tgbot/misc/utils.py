async def remove_message(func, **kwargs):
    try:
        await func(**kwargs)
    except:
        pass


import asyncio
from aiogram import Bot
from aiogram.fsm.context import FSMContext
from typing import Callable, Optional


async def remove_message(delete_method: Callable, chat_id: int = None, message_id: int = None):
    """
    Удаляет сообщение, безопасно обрабатывая ошибки.
    :param delete_method: delete_message метод бота
    :param chat_id: id чата
    :param message_id: id сообщения
    """
    try:
        if chat_id and message_id:
            await delete_method(chat_id=chat_id, message_id=message_id)
    except Exception:
        pass


def set_delayed_message(chat_id: int, delay: int, text: str, bot: Optional[Bot] = None, state: Optional[FSMContext] = None,
                        state_check: Optional[str] = None):
    """
    Отправляет сообщение с задержкой, если состояние пользователя не изменилось.
    :param chat_id: ID чата
    :param delay: задержка в секундах
    :param text: текст сообщения
    :param bot: объект бота
    :param state: FSMContext
    :param state_check: проверяемое состояние. Если пользователь уже не в этом состоянии — не отправляем
    """

    async def _send():
        await asyncio.sleep(delay)
        if state and state_check:
            current_state = await state.get_state()
            if current_state != state_check:
                # Состояние изменилось — не отправляем
                return
        if bot:
            await bot.send_message(chat_id, text)
    
    # Запускаем таск в фоне
    asyncio.create_task(_send())
