import pytz
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..remind_db.db_connect import ReminderDB
from app.remind_db.db_models import User, Reminder
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
                reminder.close_engine()
                return time_zone
            except Exception as e:
                logger.info(f'Попытка соединения: {attempt + 1}, Не удалось подключиться, переподключаемся')
                reminder.close_engine()
                if attempt == max_attempts - 1:
                    logger.error(f'Не удалось подключиться к базе. Количество попыток: {attempt}, ошибка: {e}')
                return False


async def get_user_reminder(tg_user_id):
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            async with AsyncSession(reminder.get_engine()) as db:
                logger.info(f'Ищем события пользователя')
                result_select = await db.execute(select(Reminder).filter(Reminder.tg_user_id == tg_user_id))
                events = result_select.scalars().all()
                if events:
                    return [(event.reminder_message, event.reminder_date,
                             event.tg_user_id, event.time_zone, event.reminder_id) for event in events]
                return []
        except Exception as e:
            logger.error(f'При поиске событий произошла ошибка: {e}')
            reminder.close_engine()
            if attempt == max_attempts - 1:
                logger.error(f'Не удалось подключиться к базе. Количество попыток: {attempt}, ошибка: {e}')
                return []


async def add_reminder_to_db(tg_user_id, time_zone, message, reminder_date):
    async with AsyncSession(reminder.get_engine()) as db:
        try:
            logger.info('Записываем событие в БД')
            event = Reminder(
                tg_user_id=tg_user_id,
                time_zone=time_zone,
                reminder_message=message,
                reminder_date=reminder_date.replace(tzinfo=None),
                reminder_id=f'{tg_user_id}_to_{reminder_date}'
            )
            db.add(event)
            await db.commit()
            await db.refresh(event)
            return event
        except Exception as e:
            await db.rollback()
            logger.error(f'Ошибка при записи события: {e}')


async def del_reminder(reminder_id):
    async with AsyncSession(reminder.get_engine()) as db:
        try:
            logger.info(f'Ищем событие дял удаления')
            result_select = await db.execute(select(Reminder).filter(Reminder.reminder_id == reminder_id))
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
            reminder.close_engine()
            if attempt == max_attempts - 1:
                logger.error(f'Не удалось подключиться к базе. Количество попыток: {attempt}, ошибка: {e}')
                return []