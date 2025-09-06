import pytz
from pytz import FixedOffset
from app.remind_db.db_excecuter import get_all_users, get_user_date_reminder, del_date_reminder
from app.app.deferred_task import add_one_reminder_to_scheduler, add_cron_reminder_to_scheduler
from datetime import datetime
from logger_config import get_logger


logger = get_logger(__name__)


async def restart_task():
    try:
        logger.info('Проеряем пользователей')
        users = await get_all_users()
        if not users:
            logger.info('Пользователи не найдены')
            return

        for user in users:
            logger.info('Смотрим есть ли у пользователя актуальные события')
            reminders_date = await get_user_date_reminder(user)

            if reminders_date:
                for reminder in reminders_date:
                    tz = FixedOffset(reminder[3])
                    try:
                        reminder_date = datetime.fromisoformat(reminder[1])
                        datetime_now = tz.localize(datetime.now())
                        if reminder_date.replace(tzinfo=tz) > datetime_now:
                            logger.info('Восстанавливаем актуальное разовое событие')
                            await add_one_reminder_to_scheduler(reminder[0], reminder[1], reminder[2], reminder[3])
                        else:
                            logger.info('Удаляем неактуальное разовое событие')
                            await del_date_reminder(reminder[4])
                    except Exception:
                        try:
                            await add_cron_reminder_to_scheduler(reminder[0], reminder[1], reminder[2], reminder[3])
                            await del_date_reminder(reminder[4])
                        except Exception as e:
                            logger.error(f'При восстановлении события по расписанию произошла ошибка: {e}')
        return
    except Exception as e:
        logger.error(f'При воссстановление событий произошла ошибка: {e}')
