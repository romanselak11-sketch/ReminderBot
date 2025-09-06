from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from app.app.keyboards import keyboard as kb, type_reminder as tr
from app.app.states import ReminderStates
from aiogram.fsm.context import FSMContext
from app.app.deferred_task import (add_one_reminder_to_scheduler, get_all_user_reminders,
                                   get_id_all_user_reminders, del_user_reminders, add_cron_reminder_to_scheduler)
from app.app.parse_time import parse_time_zone, parse_text_in_date, parse_text_in_cron
from app.remind_db.db_excecuter import add_user_to_db, get_user_timezone, del_date_reminder
from logger_config import get_logger
from app.app.help import description

router = Router()
condition = ReminderStates()
logger = get_logger(__name__)


@router.message(CommandStart())
async def cmd_start(message: Message):
    logger.info(f'С ботом начал работу пользователь: {message.from_user.id}')
    await message.answer(f'\U0001F91D {message.from_user.first_name or 'Уважаемый'}, приветствую!\n\nМеня зовут '
                        f'SelAK и я бот-напоминалка.\U0001f916 \n\n'
                        f'\U0001F4CCПеред началом работы, изучи инструкцию по работе, для этого ткни \U0001F449 '
                        f'/help или кнопку "Помощь" ниже \U0001F447',
                        reply_markup=kb)

@router.message(Command('timezone'))
async def add_timezone(message: Message, state: FSMContext):
    logger.info(f'Пользователь: {message.from_user.id} начал настройку часового пояса')
    await state.set_state(condition.timezone)
    await message.answer('\U000023F0 Введите ваш часовой пояс в формате: +5:00 или +05:00\n\n'
                         'Пример: Для Москвы и Московской области часовой пояс: +3:00 или +03:00',
                         reply_markup=kb)


@router.message(condition.timezone)
async def add_timezone_to_db(message: Message, state: FSMContext):
    logger.info(f'Пользователь ввел {message.text}, переводим в нужный формат')
    time_zone = await parse_time_zone(message.text)
    if not time_zone:
        logger.info(f'Неудалось обработать введенный текст: {message.text}')
        await message.answer('Вы указали неверный формат часового пояса')
        logger.info(f'Начинаем запрашивать временную зону повторно')
        await add_timezone(message, state)
        return
    else:
        try:
            logger.info(f'Сохраняем для пользователя {message.from_user.id}, часовой пояс: {time_zone}')
            await add_user_to_db(message.from_user.id, time_zone)
            await message.answer(f'\U0001F44C Часовой пояс сохранён!\n\n'
                                 f'Для создания события ткни \U0001F449 /create или "Новое событие" \U0001F447', reply_markup=kb)
        except Exception:
            await message.answer(f'\U0001F61E При сохранении данных произошла ошибка')
    await state.clear()


@router.message(Command('create'))
async def cmd_create(message: Message):
    logger.info(f'Пользователь {message.from_user.id} начал создавать событие')
    await message.answer(f'\U0000270D Выбери тип события', reply_markup=tr)


@router.callback_query(F.data == 'date')
async def cmd_date(callback: CallbackQuery, state: FSMContext):
    logger.info(f'Пользователь {callback.message.from_user.id} выбрал Разовое напоминание')
    await callback.answer()
    await state.set_state(condition.date_messages)
    await callback.message.edit_text('\U0000270D О чём напомнить?')


@router.message(condition.date_messages)
async def reminder_date(message: Message, state: FSMContext):
    logger.info(f'Пользователь прислал нам событие, о котором нужно напоминть: {message.text}')
    await state.update_data(message=message.text)
    await state.set_state(condition.date_reminder_date)
    logger.info(f'Спрашиваем у пользователя дату')
    await message.answer(f'\U000023F0 Когда напомнить?\n\n')


@router.message(condition.date_reminder_date)
async def add_reminder(message: Message, state: FSMContext):
    await state.update_data(reminder_date=message.text)
    data = await state.get_data()
    logger.info(f'Парсим сообщение  полученное от пользователя: {data['reminder_date']} в дату')

    try:
        parse_date = await parse_text_in_date(data['reminder_date'])
    except Exception as e:
        logger.error(f'При обработке даты {data["reminder_date"]} была получена ошибка: {e}')
        await message.answer(f'К сожалению я не смог найти нужную дату \U0001FAE3 \n\n'
                             f'Напиши дату в другом формате \U0001F64F')
        await state.set_state(condition.date_messages)
        await reminder_date(message, state)
        return

    try:
        time_zone = await get_user_timezone(message.chat.id)
        if not time_zone:
            await message.answer(f'\U00002639 Ты не указал свой часовой пояс!\n\n'
                                 f'Настрой свой часовой пояс тут \U0001F449 /timezone и повтори поптыку')
            await state.clear()
        else:
            logger.info('Добавляем событие в очередь>')
            await add_one_reminder_to_scheduler(data['message'], parse_date, message.chat.id, time_zone)
            await message.answer(f'\U0001FAF0 Событие добавлено!')
            logger.info('Событие добавлено')
    except Exception as e:
        logger.info(f'Не удалось сохранить событие, ошибка: {e}')
        await message.answer(f'\U0001F61E Упс, произошла ошибка. Повторите попытку')

    await state.clear()


@router.callback_query(F.data == 'cron')
async def cmd_date(callback: CallbackQuery, state: FSMContext):
    logger.info(f'Пользователь {callback.message.from_user.id} выбрал напомнинаие по расписанию')
    await callback.answer()
    await state.set_state(condition.cron_messages)
    await callback.message.edit_text('\U0000270D О чём напоминать?')

@router.message(condition.cron_messages)
async def reminder_date(message: Message, state: FSMContext):
    logger.info(f'Пользователь прислал нам событие, о котором нужно напоминть: {message.text}')
    await state.update_data(message=message.text)
    await state.set_state(condition.cron_reminder_date)
    logger.info(f'Спрашиваем у пользователя дату')
    await message.answer(f'\U000023F0 Когда напоминать?\n\n')


@router.message(condition.cron_reminder_date)
async def add_cron(message: Message, state: FSMContext):
    await state.update_data(reminder_date=message.text)
    data = await state.get_data()
    logger.info(f'Парсим сообщение  полученное от пользователя: {data['reminder_date']} в дату')

    try:
        parse_date = await parse_text_in_cron(data['reminder_date'])
    except Exception as e:
        logger.error(f'При обработке даты {data["reminder_date"]} получена ошибка: {e}')
        await message.answer(f'К сожалению я не смог найти нужную дату \U0001FAE3 \n\n'
                             f'Напиши дату в другом формате \U0001F64F')
        await state.set_state(condition.cron_messages)
        await reminder_date(message, state)
        return
    try:
        time_zone = await get_user_timezone(message.chat.id)
        if not time_zone:
            await message.answer(f'\U00002639 Ты не указал свой часовой пояс!\n\n'
                                 f'Настрой свой часовой пояс тут \U0001F449 /timezone и повтори поптыку')
            await state.clear()
        else:
            logger.info('Добавляем событие в очередь>')
            await add_cron_reminder_to_scheduler(data['message'], parse_date, message.chat.id, time_zone)
            await message.answer(f'\U0001FAF0 Событие добавлено!')
            logger.info('Событие добавлено')
    except Exception as e:
        logger.info(f'Не удалось сохранить событие, ошибка: {e}')
        await message.answer(f'\U0001F61E Упс, произошла ошибка. Повторите попытку')

    await state.clear()
@router.message(Command('events'))
async def cmd_events(message: Message):
    logger.info('Ищем события пользователя')
    try:
        reminders = await get_all_user_reminders(message.chat.id)
        if reminders:
            await message.answer(f'Твои события:\n{"\n".join(reminders)}')
        else:
            await message.answer(f'У тебя нет активных событий')
    except Exception as e:
        await message.answer(f'При поиске произошёл погром. Повтори попытку позднее')


@router.message(Command('delete'))
async def cmd_delete(message: Message, state: FSMContext):
    await state.set_state(condition.reminder_delete)
    reminders = await get_all_user_reminders(message.chat.id)
    if reminders:
        await message.answer(f'Введи порядковый номер события, которого необходимо удалить')
        await message.answer(f'{"\n".join(reminders)}')
    else:
        await message.answer(f'У тебя нет активных событий')
        await state.clear()


@router.message(condition.reminder_delete)
async def reminder_delete(message: Message, state: FSMContext):
    reminders = await get_id_all_user_reminders(message.chat.id)
    await state.update_data(remind_id=message.text)

    data = await state.get_data()
    logger.info(reminders)
    if reminders[int(data['remind_id']) - 1]:
        try:
            await del_user_reminders(reminders[int(data['remind_id']) - 1])
            await del_date_reminder(reminders[int(data['remind_id']) - 1])
            await message.answer(f'Событие удалено!')
            await state.clear()
        except Exception:
            await message.answer(f'Упс, не получилось. Повтори попытку позже')
            await state.clear()
    else:
        await message.answer(f'События с таким ID не найдено')
        await state.clear()


@router.message(Command('help'))
async def cmd_help(message: Message):
    await message.answer(f'{description}', reply_markup=kb)


@router.message(F.text.lower() == 'мои события')
async def btn_events(message: Message):
    await cmd_events(message)
    return


@router.message(F.text.lower() == 'новое событие')
async def btn_create(message: Message):
    await cmd_create(message)
    return


@router.message(F.text.lower() == 'помощь')
async def btn_help(message: Message):
    await cmd_help(message)
    return


@router.message(F.text.lower() == 'удалить событие')
async def btn_delete(message: Message, state: FSMContext):
    await state.set_state(condition.reminder_delete)
    await cmd_delete(message, state)
    return


@router.message(F.text.lower().startswith('напомни'))
async def remind_my_text(message: Message, state: FSMContext):
    await state.set_state(condition.date_reminder_date)
    await state.update_data(message=message.text[message.text.find('напомни') + 8:], reminder_date=message.text)
    await add_reminder(message, state)
    return


@router.message(F.text)
async def cmd_how_are_you(message: Message):
    await message.answer('К сожалению я пока не умею работать с произвольным текстом,'
                         ' воспользуя командой \U0001F449 /help')
