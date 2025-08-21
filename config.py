import os
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
from aiogram import Bot, Dispatcher

log_date = datetime.now().strftime('%d.%m.%Y')

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))


DB_USERNAME = os.environ.get('DB_USERNAME')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT')
DB_NAME = os.environ.get('DB_NAME')
API_TOKEN = os.environ.get('API_TOKEN')

def get_async_database_url():
    return f'postgresql+asyncpg://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

def get_sync_database_url():
    return f'postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'


bot = Bot(token=API_TOKEN)
dp = Dispatcher()



scheduler = AsyncIOScheduler()


MONTHS = {
    'январь': 1, 'января': 1,
    'февраль': 2, 'февраля': 2,
    'март': 3, 'марта': 3,
    'апрель': 4, 'апреля': 4,
    'май': 5, 'мая': 5,
    'июнь': 6, 'июня': 6,
    'июль': 7, 'июля': 7,
    'август': 8, 'августа': 8,
    'сентябрь': 9, 'сентября': 9,
    'октябрь': 10, 'октября': 10,
    'ноябрь': 11, 'ноября': 11,
    'декабрь': 12, 'декабря': 12
}

WEEKDAYS = {
    'понедельник': 0,
    'вторник': 1,
    'среда': 2,
    'четверг': 3,
    'пятница': 4,
    'суббота': 5,
    'воскресенье': 6,
}