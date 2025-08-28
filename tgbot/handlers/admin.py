from datetime import datetime

import pandas as pd
from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile, Message

from database.PostgreSQL import DatabasePSQL
from tgbot.filters.admin import AdminFilter

admin_router = Router()

admin_router.message.filter(AdminFilter())


@admin_router.message(Command('admin'))
async def promocode(message: Message, state: FSMContext, db_session: DatabasePSQL):
    await message.answer("Admin Panel",)

@admin_router.message(Command('promocode'))
async def promocode(message: Message, state: FSMContext, db_session: DatabasePSQL):
    print('Промокод')
    await state.clear()
    timestamp = int(datetime.now().timestamp())
    await db_session.add_promocode(str(timestamp))

    await message.reply(f'Промокод создан:\n\n<code>{timestamp}</code>', protect_content=False)


async def xlsx(message, db):
    msg = await message.answer("Идет выгрузка базы данных...")

    writer = pd.ExcelWriter('db_data.xlsx', engine='xlsxwriter', datetime_format="YYYY-MM-DD HH:MM")
    workbook = writer.book
    center_wrap_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'text_wrap': True})

    select_all_users = await db.select_all_users_and_accesses()
    df_users = pd.DataFrame(select_all_users,
                            columns=["Telegram id", "Полное имя", '@username', "Ник пользователя", "email", 'Доступ'])
    df_users.to_excel(writer, sheet_name='Данные пользователей', index=False)
    column_widths_users = [20, 25, 23, 25, 25, 25]
    for i, width in enumerate(column_widths_users):
        writer.sheets['Данные пользователей'].set_column(i, i, width, center_wrap_format)

    # _____________________
    select_all_tickets = await db.select_all_tickets()
    df_users = pd.DataFrame(select_all_tickets,
                            columns=["Telegram id (от кого)", "Билет", "Telegram id(пришел)", "Дата перехода"])
    df_users.to_excel(writer, sheet_name='Билеты', index=False)
    column_widths_users = [30, 30, 30, 30]
    for i, width in enumerate(column_widths_users):
        writer.sheets['Билеты'].set_column(i, i, width, center_wrap_format)

    # _____________________
    select_all_impression = await db.select_all_impression()
    df_users = pd.DataFrame(select_all_impression,
                            columns=["id записи", "Telegram id", "Текст"])
    df_users.to_excel(writer, sheet_name='Впечатления пользователей', index=False)
    column_widths_users = [20, 25, 40]
    for i, width in enumerate(column_widths_users):
        writer.sheets['Впечатления пользователей'].set_column(i, i, width, center_wrap_format)

    # _____________________
    payments = await db.get_payments()
    df_users = pd.DataFrame(payments,
                            columns=["id записи", "Telegram id", "ID Юкасса", "Цена", "В подарок", "Статус", "Дата"])
    df_users.to_excel(writer, sheet_name='Платежи', index=False)
    column_widths_users = [20, 25, 40, 25, 25, 25, 17]
    for i, width in enumerate(column_widths_users):
        writer.sheets['Платежи'].set_column(i, i, width, center_wrap_format)

    # _____________________
    promocodes = await db.get_all_promocode()
    df_users = pd.DataFrame(promocodes,
                            columns=["id записи", "Промокод", "Telegram id"])
    df_users.to_excel(writer, sheet_name='Промокоды', index=False)
    column_widths_users = [20, 30, 30]
    for i, width in enumerate(column_widths_users):
        writer.sheets['Промокоды'].set_column(i, i, width, center_wrap_format)

    # _____________________
    writer.close()

    file = FSInputFile("db_data.xlsx")
    await msg.edit_text("Объявления из БД выгружены")
    await message.answer_document(file, protect_content=False)


@admin_router.message(Command("get_data", "/"))
async def get_data(message: Message, state: FSMContext, db_session: DatabasePSQL):
    await state.clear()
    await xlsx(message, db_session)
    
