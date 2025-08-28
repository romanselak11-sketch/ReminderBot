from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..remind_db.db_connect import ReminderDB
from app.remind_db.db_models import User, ReminderDate, ReminderTrigger, ReminderInterval
from logger_config import get_logger

logger = get_logger(__name__)

reminder = ReminderDB()


async def add_user_to_db(tg_user_id, time_zone):
    async with AsyncSession(reminder.get_engine()) as db:
        try:
            search_user = await db.execute(select(User).filter(User.tg_user_id == tg_user_id))
            result = search_user.scalar_one_or_none()
            logger.info(f'Найдено: {result}')
            if result:
                logger.info(f'Корректируем часовой пояс у пользователя: {tg_user_id}')
                result.time_zone = time_zone
                mg_user_reminder = result
            else:
                logger.info(f'Добавление пользователя {tg_user_id} а базу')
                user_reminder = User(
                    tg_user_id=tg_user_id,
                    time_zone=time_zone
                )
                mg_user_reminder = await db.merge(user_reminder)
            await db.commit()
            await db.refresh(mg_user_reminder)
            return mg_user_reminder

        except Exception as e:
            await db.rollback()
            logger.error(f'Ошибка при добавлении записи в базу {e}')


async def get_user_timezone(tg_user_id):
    max_attempts = 3
    for attempt in range(max_attempts):
        async with AsyncSession(reminder.get_engine()) as db:
            try:
                logger.info(f'Ищем временную зону для пользователя: {tg_user_id}')
                result_select = await db.execute(select(User.time_zone).filter(User.tg_user_id == tg_user_id))
                time_zone = result_select.scalar_one_or_none()
                logger.info(f'Временная зона найдена: {time_zone}')
                await reminder.close_engine()
                return time_zone
            except Exception as e:
                logger.info(f'Попытка соединения: {attempt + 1}, Не удалось подключиться, переподключаемся')
                await reminder.close_engine()
                if attempt == max_attempts - 1:
                    logger.error(f'Не удалось подключиться к базе. Количество попыток: {attempt}, ошибка: {e}')
                return False


async def add_date_reminder_to_db(tg_user_id, time_zone, message, reminder_date, reminder_id):
    async with AsyncSession(reminder.get_engine()) as db:
        try:
            logger.info('Записываем событие в БД')
            event = ReminderDate(
                tg_user_id=tg_user_id,
                time_zone=time_zone,
                reminder_message=message,
                reminder_date=reminder_date.replace(tzinfo=None),
                reminder_id=reminder_id
            )
            db.add(event)
            await db.commit()
            await db.refresh(event)
            return event
        except Exception as e:
            await db.rollback()
            logger.error(f'Ошибка при записи события: {e}')


async def get_user_date_reminder(tg_user_id):
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            async with AsyncSession(reminder.get_engine()) as db:
                logger.info(f'Ищем события пользователя')
                result_select = await db.execute(select(ReminderDate).filter(ReminderDate.tg_user_id == tg_user_id))
                events = result_select.scalars().all()
                if events:
                    return [(event.reminder_message, event.reminder_date,
                             event.tg_user_id, event.time_zone, event.reminder_id) for event in events]
                return []
        except Exception as e:
            logger.error(f'При поиске событий произошла ошибка: {e}')
            await reminder.close_engine()
            if attempt == max_attempts - 1:
                logger.error(f'Не удалось подключиться к базе. Количество попыток: {attempt}, ошибка: {e}')
                return []


async def del_date_reminder(reminder_id):
    async with AsyncSession(reminder.get_engine()) as db:
        try:
            logger.info(f'Ищем событие для удаления')
            result_select = await db.execute(select(ReminderDate).filter(ReminderDate.reminder_id == reminder_id))
            event = result_select.scalar_one_or_none()
            if event:
                logger.info(f'Удаляем событие: {reminder_id}')
                await db.delete(event)
                await db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f'При удалении события произошла ошибка {e}')
            await db.rollback()
            return False


async def add_interval_reminder_to_db(tg_user_id, message, interval, reminder_id):
    async with AsyncSession(reminder.get_engine()) as db:
        try:
            logger.info('Записываем событие в БД')
            event = ReminderInterval(
                tg_user_id=tg_user_id,
                reminder_message=message,
                reminder_id=reminder_id,
                interval=str(interval)
            )
            db.add(event)
            await db.commit()
            await db.refresh(event)
            return event
        except Exception as e:
            await db.rollback()
            logger.error(f'Ошибка при записи события: {e}')


async def get_user_interval_reminder(tg_user_id):
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            async with AsyncSession(reminder.get_engine()) as db:
                logger.info(f'Ищем события пользователя')
                result_select = await db.execute(select(ReminderInterval).filter(ReminderInterval.tg_user_id == tg_user_id))
                events = result_select.scalars().all()
                logger.info(f'Проверка ответа: {events}')
                logger.info(f'Проверка ответа: {[(event.reminder_message, event.interval, event.reminder_id) for event in events]}')
                if events:
                    return [(event.reminder_message, event.interval, event.reminder_id) for event in events]
                return []
        except Exception as e:
            logger.error(f'При поиске событий произошла ошибка: {e}')
            await reminder.close_engine()
            if attempt == max_attempts - 1:
                logger.error(f'Не удалось подключиться к базе. Количество попыток: {attempt}, ошибка: {e}')
                return []


async def get_all_users():
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            async with AsyncSession(reminder.get_engine()) as db:
                logger.info(f'Ищем пользователей')
                result_select = await db.execute(select(User))
                users = [user.tg_user_id for user in result_select.scalars().all()]
                if users:
                    return users
                else:
                    return []
        except Exception as e:
            logger.error(f'При поиске пользователей произошла ошибка: {e}')
            await reminder.close_engine()
            if attempt == max_attempts - 1:
                logger.error(f'Не удалось подключиться к базе. Количество попыток: {attempt}, ошибка: {e}')
                return []