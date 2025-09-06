from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)


keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Мои события'), KeyboardButton(text='Новое событие')],
    [KeyboardButton(text='Удалить событие'), KeyboardButton(text='Помощь')]
], resize_keyboard=True, input_field_placeholder='Выберите действие из меню', is_persistent=True)

type_reminder = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Разовое', callback_data='date'),
     InlineKeyboardButton(text='По расписанию', callback_data='cron')]
])






