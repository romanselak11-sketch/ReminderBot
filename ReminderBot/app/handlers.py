from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from random import randint

from app.keyboards import inline_keyboard as kb

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.reply(f'Привет, {message.from_user.first_name}!\nДля того, чтобы узнать что я умею отправь команду /help',
                        reply_markup=kb)


@router.message(Command('help'))
async def cmd_help(message: Message):
    await message.answer('Я могу спросить у звезд число, для этого воспользуйся командой /random')


@router.message(Command('random'))
async def cmd_random(message: Message):
    await message.answer(f'Звёзды загадали число: {randint(1, 100)}')



@router.message(F.text)
async def cmd_how_are_you(message: Message):
    await message.answer('К сожалению я пока не умею работать с произвольным текстом, но я учусь ^_^')
