import contextlib
from typing import Optional, AsyncIterator
from datetime import datetime, timedelta
import json


import asyncpg


class DatabasePSQL:
    def __init__(self, config):
        self._pool: Optional[asyncpg.Pool] = None
        self.config = config

    async def create_table_users(self):
        sql = """
        CREATE TABLE IF NOT EXISTS users (
        telegram_id BIGINT PRIMARY KEY,
        full_name VARCHAR(255) NOT NULL,
        username varchar(255) NULL,
        entered_name varchar(255) NULL,
        mail VARCHAR(255) NULL UNIQUE  
        );
        """
        await self.execute(sql, execute=True)

    async def create_table_tickets(self):
        sql = """
        CREATE TABLE IF NOT EXISTS tickets (
        id SERIAL PRIMARY KEY,
        creator_id BIGINT NOT NULL,
        user_id BIGINT NULL,
        ticket BIGINT,
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW(),
        FOREIGN KEY (creator_id) REFERENCES users (telegram_id),
        FOREIGN KEY (user_id) REFERENCES users (telegram_id)
        );
        """
        await self.execute(sql, execute=True)

    async def create_table_impressions(self):
        sql = """
        CREATE TABLE IF NOT EXISTS impressions (
        id SERIAL PRIMARY KEY,
        user_id BIGINT NOT NULL,
        text TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (telegram_id)
        );
        """
        await self.execute(sql, execute=True)

    async def create_table_payments(self):
        sql = """
        CREATE TABLE IF NOT EXISTS payments (
        id SERIAL PRIMARY KEY,
        pay_id VARCHAR(255) NOT NULL,
        amount DECIMAL,
        gift BOOLEAN,
        status VARCHAR(50) DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW(),
        user_id BIGINT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (telegram_id)
        );
        """  # status=pending or succeeded or canceled
        await self.execute(sql, execute=True)

    async def create_table_accesses(self):
        sql = """
        CREATE TABLE IF NOT EXISTS accesses (
        id SERIAL PRIMARY KEY,
        user_id BIGINT NOT NULL UNIQUE,
        FOREIGN KEY (user_id) REFERENCES users (telegram_id)
        );
        """  # status=pending or succeeded or canceled
        await self.execute(sql, execute=True)

    async def create_table_promocode(self):
        sql = """
            CREATE TABLE IF NOT EXISTS promocode (
                id SERIAL PRIMARY KEY,
                code VARCHAR(255) NOT NULL UNIQUE,
                user_id BIGINT UNIQUE,
                FOREIGN KEY (user_id) REFERENCES users (telegram_id)
        );
        """
        await self.execute(sql, execute=True)

    async def create_table_offline_reminders(self):
        sql = """
        CREATE TABLE IF NOT EXISTS offline_reminders (
            user_id BIGINT PRIMARY KEY,
            event_datetime TIMESTAMP NOT NULL,
            purchase_datetime TIMESTAMP NOT NULL,
            last_sent TIMESTAMP,
            step SMALLINT DEFAULT 0,
            buttons_clicked BOOLEAN DEFAULT FALSE,
            purchased BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (user_id) REFERENCES users (telegram_id)
        );
        """
        await self.execute(sql, execute=True)
    async def create_table_reminders(self):
        sql = """
        CREATE TABLE IF NOT EXISTS reminders (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            send_at TIMESTAMP NOT NULL,
            type VARCHAR(50) NOT NULL,       -- что за напоминание (email, трек, оплата, оффлайн)
            status VARCHAR(20) DEFAULT 'pending',  -- pending / sent / canceled
            payload JSONB NULL               -- дополнительные данные для напоминания
        );
        """
        await self.execute(sql, execute=True)

    async def add_reminder(self, user_id, reminder_type, delay_seconds, payload=None):
        send_at = datetime.utcnow() + timedelta(seconds=delay_seconds)
        payload_json = json.dumps(payload) if payload else None

        sql = """
        INSERT INTO reminders (user_id, send_at, type, payload)
        VALUES ($1, $2, $3, $4)
        """
        await self.execute(sql, user_id, send_at, reminder_type, payload_json, execute=True)

    async def cancel_reminder(self, user_id, reminder_type=None):
        if reminder_type:
            await self.execute(
                "UPDATE reminders SET status='canceled' WHERE user_id=$1 AND type=$2 AND status='pending'",
                user_id, reminder_type, execute=True
            )
        else:
            await self.execute(
                "UPDATE reminders SET status='canceled' WHERE user_id=$1 AND status='pending'",
                user_id, execute=True
            )

    async def mark_as_purchased(self, user_id: int):
        """
        Помечаем, что пользователь купил билет (исключаем его из рассылок).
        """
        sql = "UPDATE offline_reminders SET purchased=TRUE WHERE user_id=$1"
        await self.execute(sql, user_id, execute=True)

    async def is_purchased(self, user_id: int) -> bool:
        """
        Проверяем, купил ли пользователь билет.
        """
        sql = "SELECT purchased FROM offline_reminders WHERE user_id=$1"
        result = await self.execute(sql, user_id, fetchrow=True)
        return result and result["purchased"]


    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join([
            f"{item} = ${num}" for num, item in enumerate(parameters.keys(),
                                                          start=1)
        ])
        return sql, tuple(parameters.values())

    async def add_user(self, full_name, username, telegram_id):
        sql = "SELECT * FROM users WHERE telegram_id=$1"
        print('делаем add')
        result = await self.execute(sql, telegram_id, fetchrow=True)
        print('Result')
        print(result)
        if not result:
            print('Добавил')
            sql = "INSERT INTO users (full_name, username, telegram_id) VALUES($1, $2, $3) returning *"
            await self.execute(sql, full_name, username, telegram_id, execute=True)

    async def select_all_users(self):
        sql = "SELECT * FROM users"
        return await self.execute(sql, fetch=True)

    async def select_all_users_and_accesses(self):
        sql = """
            SELECT
                u.*,
                CASE
                    WHEN a.user_id IS NOT NULL THEN '✅'
                    ELSE '❌'
                END AS accesse
            FROM
                users u
            LEFT JOIN
                accesses a
            ON
                u.telegram_id = a.user_id;
        """
        return await self.execute(sql, fetch=True)

    async def select_all_tickets(self):
        sql = "SELECT creator_id, ticket, user_id, updated_at FROM tickets"
        return await self.execute(sql, fetch=True)

    async def add_ticket(self, telegram_id, ticket):
        sql = "INSERT INTO tickets (creator_id, ticket) VALUES($1, $2)"
        await self.execute(sql, telegram_id, ticket, execute=True)

    async def get_ticket(self, ticket, telegram_id):
        sql = "SELECT * FROM tickets WHERE ticket=$1 and creator_id!=$2 and user_id is NULL"
        return await self.execute(sql, ticket, telegram_id, fetchrow=True)

    async def update_ticket(self, ticket, telegram_id, date):
        sql = "UPDATE tickets SET user_id=$2, updated_at=$3 WHERE ticket=$1"
        await self.execute(sql, ticket, telegram_id, date, execute=True)

    async def select_buyer_with_name_and_email(self, telegram_id):
        sql = ("SELECT user_id FROM accesses a JOIN users u "
               "ON a.user_id = u.telegram_id WHERE u.telegram_id = $1 "
               "AND u.entered_name IS NOT NULL;")
        return await self.execute(sql, telegram_id, fetchrow=True)

    async def add_impression(self, telegram_id, text):
        sql = "INSERT INTO impressions (user_id, text) VALUES($1, $2) returning *"
        return await self.execute(sql, telegram_id, text, execute=True)

    async def select_impression(self, **kwargs):
        sql = "SELECT * FROM impressions WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetch=True)

    async def select_all_impression(self):
        sql = "SELECT * FROM impressions"
        return await self.execute(sql, fetch=True)

    async def select_user(self, **kwargs):
        sql = "SELECT * FROM users WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def count_users(self):
        sql = "SELECT COUNT(*) FROM users"
        return await self.execute(sql, fetchval=True)

    async def get_mail_user(self, telegram_id):
        sql = "SELECT mail FROM users WHERE telegram_id=$1"
        return await self.execute(sql, telegram_id, fetchrow=True)

    async def update_mail_user(self, mail, telegram_id):
        sql = "UPDATE users SET mail=$1 WHERE telegram_id=$2"
        return await self.execute(sql, mail, telegram_id, execute=True)

    async def update_entered_name_user(self, name, telegram_id):
        sql = "UPDATE users SET entered_name=$1 WHERE telegram_id=$2"
        return await self.execute(sql, name, telegram_id, execute=True)

    async def update_user_username(self, username, telegram_id):
        sql = "UPDATE users SET username=$1 WHERE telegram_id=$2"
        return await self.execute(sql, username, telegram_id, execute=True)

    async def create_payment(self, telegram_id, amount, gift, pay_id):
        sql = "INSERT INTO payments (user_id, amount, gift, pay_id) VALUES($1, $2, $3, $4) "
        await self.execute(sql, telegram_id, amount, gift, pay_id, execute=True)

    async def get_payment(self, pay_id):
        sql = "SELECT * FROM payments WHERE pay_id=$1"
        return await self.execute(sql, pay_id, fetchrow=True)

    async def get_payments(self):
        sql = """
            SELECT id,
                   user_id,
                   pay_id,
                   amount,
                   CASE
                       WHEN gift IS TRUE THEN 'Да'
                       ELSE 'Нет'
                       END AS gift,
                   CASE
                       WHEN status = 'succeeded' THEN 'Оплачено'
                       ELSE 'Не оплачено'
                       END AS status,
                   updated_at
            FROM payments
            where status = 'succeeded';
        """
        return await self.execute(sql, fetch=True)

    async def update_payment_status(self, pay_id, status, date):
        sql = "UPDATE payments SET status=$2, updated_at=$3 WHERE pay_id=$1"
        await self.execute(sql, pay_id, status, date, execute=True)

    async def add_accesses(self, telegram_id):
        sql = "INSERT INTO accesses (user_id) VALUES($1)"
        await self.execute(sql, telegram_id, execute=True)

    async def get_accesses(self, telegram_id):
        sql = "SELECT * FROM accesses WHERE user_id=$1"
        return await self.execute(sql, telegram_id, fetchrow=True)

    async def add_promocode(self, code):
        sql = "INSERT INTO promocode (code) VALUES($1)"
        return await self.execute(sql, code, execute=True)

    async def get_all_promocode(self):
        sql = "SELECT * FROM promocode"
        return await self.execute(sql, fetch=True)

    async def get_promocode_by_code(self, code):
        sql = "SELECT * FROM promocode WHERE code=$1 and user_id is NULL"
        return await self.execute(sql, code, fetchrow=True)

    async def update_promocode(self, code, user_id):
        sql = "UPDATE promocode SET user_id=$2 where code=$1"
        await self.execute(sql, code, user_id, execute=True)

    async def delete_users(self):
        await self.execute("DELETE FROM users WHERE TRUE", execute=True)

    async def drop_users(self):
        await self.execute("DROP TABLE IF EXISTS users CASCADE", execute=True)

    async def drop_tickets(self):
        await self.execute("DROP TABLE IF EXISTS tickets", execute=True)

    async def drop_impressions(self):
        await self.execute("DROP TABLE IF EXISTS impressions", execute=True)

    async def drop_payments(self):
        await self.execute("DROP TABLE IF EXISTS payments", execute=True)

    async def drop_accesses(self):
        await self.execute("DROP TABLE IF EXISTS accesses", execute=True)

    async def execute(self, command, *args,
                      fetch: bool = False,
                      fetchval: bool = False,
                      fetchrow: bool = False,
                      execute: bool = False
                      ):
        async with self._transaction() as connection:  # type: asyncpg.Connection
            if fetch:
                result = await connection.fetch(command, *args)
            elif fetchval:
                result = await connection.fetchval(command, *args)
            elif fetchrow:
                result = await connection.fetchrow(command, *args)
            elif execute:
                result = await connection.execute(command, *args)
        return result

    @contextlib.asynccontextmanager
    async def _transaction(self) -> AsyncIterator[asyncpg.Connection]:
        if self._pool is None:
            self._pool = await asyncpg.create_pool(
                user=self.config.user,
                password=self.config.password,
                host=self.config.host,
                database=self.config.database,
            )
        async with self._pool.acquire() as conn:  # type: asyncpg.Connection
            async with conn.transaction():
                yield conn


    # ================== OFFLINE REMINDERS ==================

    async def add_offline_reminder(self, user_id, event_datetime, purchase_datetime):
        """
        Добавить запись о напоминании (создаётся только один раз для user_id).
        """
        sql = """
        INSERT INTO offline_reminders (user_id, event_datetime, purchase_datetime)
        VALUES ($1, $2, $3)
        ON CONFLICT (user_id) DO NOTHING
        """
        await self.execute(sql, user_id, event_datetime, purchase_datetime, execute=True)

    async def update_last_sent(self, user_id, last_sent, step: int):
        """
        Обновить время последней отправки и шаг (0, 1, 2, 3 ...).
        """
        sql = """
        UPDATE offline_reminders
        SET last_sent=$2, step=$3
        WHERE user_id=$1
        """
        await self.execute(sql, user_id, last_sent, step, execute=True)

    async def get_user_from_db(self, user_id):
        """
        Получить данные напоминаний конкретного пользователя.
        """
        sql = "SELECT * FROM offline_reminders WHERE user_id=$1"
        return await self.execute(sql, user_id, fetchrow=True)

    async def get_all_reminders(self):
        """
        Получить все записи из offline_reminders (например, для массовых проверок APScheduler).
        """
        sql = "SELECT * FROM offline_reminders"
        return await self.execute(sql, fetch=True)

    async def mark_buttons_clicked(self, user_id: int):
        """
        Помечаем, что пользователь нажал кнопку (например, 'напомни позже').
        """
        sql = "UPDATE offline_reminders SET buttons_clicked=TRUE WHERE user_id=$1"
        await self.execute(sql, user_id, execute=True)

    async def close(self) -> None:
        if self._pool is None:
            return None

        await self._pool.close()


