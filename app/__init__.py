import asyncio
from app.app.handlers import router
from config import bot, dp, scheduler
from app.remind_db.db_connect import ReminderDB


Db = ReminderDB()


async def main():
    scheduler.start()
    dp.include_router(router)
    await dp.start_polling(bot)

try:
    asyncio.run(main())
except KeyboardInterrupt:
    print('Конец')


