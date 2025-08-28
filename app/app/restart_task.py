from pytz import FixedOffset
from app.remind_db.db_excecuter import get_all_users, get_user_date_reminder, del_date_reminder, get_user_interval_reminder
from app.app.deferred_task import add_one_reminder_to_scheduler, add_interval_reminder_to_scheduler
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
            reminders_interval = await get_user_interval_reminder(user)

            if not reminders_date and not reminders_interval:
                logger.info(f'У пользователя {user} нет разовых активных событий')
                continue

            if reminders_date:
                for reminder in reminders_date:
                    tz = FixedOffset(reminder[3])
                    reminder_date = tz.localize(reminder[1])
                    datetime_now = tz.localize(datetime.now())
                    if reminder_date > datetime_now:
                        logger.info('Восстанавливаем актуальное разовое событие')
                        await add_one_reminder_to_scheduler(reminder[0], reminder[1], reminder[2], reminder[3])
                    else:
                        logger.info('Удаляем неактуальное разовое событие')
                        await del_date_reminder(reminder[4])

            if reminders_interval:
                for reminder in reminders_interval:
                    logger.info('Восстанавливаем интервальное событие')
                    await add_interval_reminder_to_scheduler(reminder[0], reminder[1], reminder[2])

        return
    except Exception as e:
        logger.error(f'При воссстановление заданий произошла ошибка: {e}')


if __name__ == '__main__':
    restart_task()