from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)

keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Мои напоминания'), KeyboardButton(text='Новое напоминание')]
], resize_keyboard=True, input_field_placeholder='Выберите действие из меню')

inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Новое напоминание", url='https://ya.ru')]
])