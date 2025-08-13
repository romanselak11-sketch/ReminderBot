from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton)

keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Мои события'), KeyboardButton(text='Новое событие')],
    [KeyboardButton(text='Удалить событие'), KeyboardButton(text='Помощь')]
], resize_keyboard=True, input_field_placeholder='Выберите действие из меню')