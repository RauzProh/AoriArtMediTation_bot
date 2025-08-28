import asyncio
import json
import logging
from asyncio import CancelledError

import aioredis

from tgbot.misc.payments import notification_payment


class WebhookReader:
    @classmethod
    async def handle_payment_callback(cls, data, db):
        await notification_payment(data, db)

    @classmethod
    async def reader(cls, db):

        redis = aioredis.from_url("redis://localhost", db=1)
        channel = "payment_channel"  # канал для прослушивания

        while True:
            try:
                # Ожидаем сообщения из Redis канала
                message = await redis.lpop(channel)

                if message is None:
                    await asyncio.sleep(10)
                    continue

                data = json.loads(message)
                await cls.handle_payment_callback(data, db)

            except asyncio.TimeoutError:
                pass
            except CancelledError:
                return

            except:
                logging.exception('Error:')
                pass

            await asyncio.sleep(10)