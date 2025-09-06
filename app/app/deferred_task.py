from pytz import FixedOffset
from config import scheduler
from app.app.response_handlers import user_response
from logger_config import get_logger
from app.remind_db.db_excecuter import add_date_reminder_to_db
from uuid import uuid4

logger = get_logger(__name__)


async def add_one_reminder_to_scheduler(message, reminder_date, chat_id, time_zone):
    tz = FixedOffset(time_zone)
    reminder_date = tz.localize(reminder_date)
    _id = str(uuid4())
    try:
        try:
            await add_date_reminder_to_db(chat_id, time_zone, message, reminder_date, _id)
        except Exception as e:
            logger.error(f'При записи события в Бд произошла ошибкка: {e}')

        scheduler.add_job(
            func=user_response,
            trigger='date',
            run_date=reminder_date,
            args=(chat_id, message, _id),
            id=_id,
            misfire_grace_time=30,
            coalesce=True,
            max_instances=5
        )
    except Exception as e:
        logger.error(f'При добавлении напоминания, произошла ошибка: {e}')
        return Exception


async def add_cron_reminder_to_scheduler(message, reminder_date, chat_id, time_zone):
    tz = FixedOffset(time_zone)
    minute, hour, day, month, weekday = reminder_date.split(' ')
    _id = str(uuid4())
    try:
        try:
            await add_date_reminder_to_db(chat_id, time_zone, message, reminder_date, _id)
        except Exception as e:
            logger.error(f'При записи события в Бд произошла ошибкка: {e}')

        scheduler.add_job(
            func=user_response,
            trigger='cron',
            minute=minute,
            hour=hour,
            day=day,
            month=month,
            day_of_week=weekday,
            args=(chat_id, message, _id),
            id=_id,
            timezone=tz,
            replace_existing=True
        )
    except Exception as e:
        logger.error(f'При добавлении напоминания, произошла ошибка: {e}')
        return Exception


async def get_all_user_reminders(chat_id):
    logger.info(f'Ищем события в планировщике')
    try:
        all_reminders = scheduler.get_jobs()
        logger.info(all_reminders)
        all_user_reminders = [
            f'Дата: {reminder.next_run_time}, Событие: {reminder.args[1]}'
            for reminder in all_reminders if chat_id == reminder.args[0]]
        logger.info(all_user_reminders)
        if all_user_reminders:
            return [f'\U000023F0 {key + 1}) {reminder}' for key, reminder in enumerate(all_user_reminders)]
        else:
            return False
    except Exception as e:
        logger.error(f'При поиске произошла ошибка: {e}')
        raise Exception


async def get_id_all_user_reminders(chat_id):
    logger.info(f'Ищем id события для пользователя {chat_id}')
    try:
        all_reminders = scheduler.get_jobs()
        all_user_reminders = [reminder.id for reminder in all_reminders if chat_id == reminder.args[0]]

        if all_user_reminders:
            return all_user_reminders
        else:
            return []
    except Exception as e:
        logger.error(f'При поиске событий произошла ошибка: {e}')
        raise Exception


async def del_user_reminders(job_id):
    logger.info(f'Удалячем задачу {job_id}')
    try:
        scheduler.remove_job(job_id)
        return True
    except Exception as e:
        logger.error(f'При удалении задачи возникла ошибка: {e}')
        return False

