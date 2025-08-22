from pytz import FixedOffset
from config import scheduler
from app.app.response_handlers import user_response
from logger_config import get_logger

logger = get_logger(__name__)


async def add_one_reminder_to_scheduler(message, reminder_date, chat_id, time_zone):
    tz = FixedOffset(time_zone)
    reminder_date = tz.localize(reminder_date)
    try:
        scheduler.add_job(
            func=user_response,
            trigger='date',
            run_date=reminder_date,
            args=(chat_id, message),
            id=f'{chat_id}_to_{reminder_date}')

    except Exception as e:
        logger.info(f'При добавлении напоминания, произошла ошибка: {e}')

async def get_all_user_reminders(chat_id):
    logger.info(f'Ищем события в планировщике')
    try:
        all_reminders = scheduler.get_jobs()
        all_user_reminders = [
            f'\U000023F0 {key + 1}) Дата: {reminder.next_run_time.strftime('%d.%m.%Y %H:%M')}, Событие: {reminder.args[1]}'
            for key, reminder in enumerate(all_reminders) if str(chat_id) in reminder.id]

        if all_user_reminders:
            return all_user_reminders
        else:
            return False
    except Exception as e:
        logger.error(f'При поиске произошла ошибка: {e}')
        raise Exception


async def get_id_all_user_reminders(chat_id):
    logger.info(f'Ищем id событий для пользователя {chat_id}')
    try:
        all_reminders = scheduler.get_jobs()
        all_user_reminders = [reminder.id for reminder in all_reminders if str(chat_id) in reminder.id]

        if all_user_reminders:
            return all_user_reminders
        else:
            return False
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

