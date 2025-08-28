from config import bot
from logger_config import get_logger
from app.remind_db.db_excecuter import del_date_reminder


logger = get_logger(__name__)

"""Нужно добавить повторную отправку уведомления, пока пользователь его не примет"""

async def user_response(chat_id, message, remider_id):
    logger.info(f'Отправляем напоминание, пользователю {chat_id}')
    await bot.send_message(chat_id=chat_id, text=f'\U0001F590 Напоминаю: {message}')
    await del_date_reminder(remider_id)




