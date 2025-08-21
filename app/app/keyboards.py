from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import InlineKeyboardBuilder


keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Мои события'), KeyboardButton(text='Новое событие')],
    [KeyboardButton(text='Удалить событие'), KeyboardButton(text='Помощь')]
], resize_keyboard=True, input_field_placeholder='Выберите действие из меню', is_persistent=True)

range_reminder_inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Сегодня', callback_data='today'), InlineKeyboardButton(text='Завтра', callback_data='tomorrow')],
    [InlineKeyboardButton(text='На этой неделе', callback_data='curren_week'), InlineKeyboardButton(text='Другая дата', callback_data='another_date')],
])






