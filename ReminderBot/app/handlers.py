from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from app.keyboards import keyboard as kb

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(f'\U0001F91D {message.from_user.first_name or 'Уважаемый'}, приветствую!\n\nМеня зовут SelAK и я бот-напоминалка.\U0001f916 '
                        f'\n\n\U0001F4CCДля начала работы выбери действие ниже \U0001F447\n\n'
                        f'\U0001F4CCДля просмотра моих возможностей ткни \U0001F449 /help или выбери действие "помощь"',
                        reply_markup=kb)




@router.message(Command('create'))
async def cmd_random(message: Message):
    await message.answer(f'Пока не умею\U0001F622')

@router.message(Command('events'))
async def cmd_random(message: Message):
    await message.answer(f'Пока не умею\U0001F622')

@router.message(Command('delete'))
async def cmd_random(message: Message):
    await message.answer(f'Пока не умею\U0001F622')

@router.message(Command('help'))
async def cmd_help(message: Message):
    await message.answer(f'\U0001F4CCДля создания события ткни \U0001F449 /create или выбери действие "Новое событие"\n\n'
                        f'\U0001F4CCДля просмотра текущих событий ткни \U0001F449 /events или выбери действие "Мои события"\n\n'
                        f'\U0001F4CCДля того что-бы удалить событие, нткни \U0001F449 /delete или выбери действие "Удалить событие"\n\n')


@router.message(F.text)
async def cmd_how_are_you(message: Message):
    await message.answer('К сожалению я пока не умею работать с произвольным текстом, но я учусь ^_^')
