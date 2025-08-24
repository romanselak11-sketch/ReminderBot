from sqlalchemy import Engine, create_engine
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy_utils import create_database, database_exists
from typing import Optional
from config import get_sync_database_url, get_async_database_url
from logger_config import get_logger
from ..remind_db.db_models import Base

logger = get_logger(__name__)


class ReminderDB:
    def __init__(self):
        self._engine: Optional[Engine] = None
        try:
            logger.info('Создаём БД')
            create_database(get_sync_database_url())
        except Exception as e:
            logger.error(f"БД уже создана или возникла ошибка при создании: {e}")
            pass
        try:
            logger.info('Создаём таблицы')
            sync_engine = create_engine(get_sync_database_url())
            Base.metadata.create_all(sync_engine)
            sync_engine.dispose()
        except Exception as e:
            logger.error(f"БД уже создана или возникла ошибка при создании: {e}")
            pass

    def get_engine(self):
        if self._engine is None:
            self._engine = create_async_engine(
                get_async_database_url(),
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
                pool_recycle=300,
                pool_timeout=30,)
        return self._engine

    async def close_engine(self):
        if self._engine:
            try:
                await self._engine.dispose()
            except Exception as e:
                logger.error(f'Ошибка при закрытии соединения: {e}')
            finally:
                self._engine = None

