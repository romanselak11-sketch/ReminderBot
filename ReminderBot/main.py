from dotenv import load_dotenv
import logging
import os
import asyncio
from aiogram import Bot, Dispatcher
from app.handlers import router
from remind_db.db_excecuter import CreateDB, CreateTable

load_dotenv()
API_TOKEN = os.getenv('API_TOKEN')

bot = Bot(token=API_TOKEN)
dp = Dispatcher()


async def main():
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    create_db = CreateDB()
    create_table = CreateTable()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Конец')



