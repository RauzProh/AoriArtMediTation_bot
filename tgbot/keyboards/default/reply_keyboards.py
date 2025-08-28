from aiogram import types
from aiogram.utils.keyboard import ReplyKeyboardBuilder

main_menu = ReplyKeyboardBuilder()

main_menu.row(types.KeyboardButton(text="Взглянуть на свои открытия"))
main_menu.row(types.KeyboardButton(text="Купить доступ в подарок"))
main_menu.row(types.KeyboardButton(text="Поделиться впечатлениями с автором"))
main_menu.row(types.KeyboardButton(text="Перейти в канал автора"))
main_menu = main_menu.as_markup(resize_keyboard=True)


