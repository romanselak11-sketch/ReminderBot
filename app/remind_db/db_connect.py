from sqlalchemy import Engine, create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy_utils import create_database
from typing import Optional
from config import get_sync_database_url, get_async_database_url
from logger_config import get_logger
from ..remind_db.db_models import Base

logger = get_logger(__name__)


class ReminderDB:
    def __init__(self):
        self._engine: Optional[Engine] = None
        logger.info('Проверяем наличие БД')
        if not self._get_db():
            logger.info('БД Не найдена')
            logger.info('Создаём БД')
            create_database(get_sync_database_url())
            try:
                logger.info('Создаём таблицы')
                sync_engine = create_engine(get_sync_database_url())
                Base.metadata.create_all(sync_engine)
                sync_engine.dispose()
            except Exception as e:
                logger.error(f"Таблицы уже созданы или возникла ошибка при создании: {e}")
        else:
            logger.error(f"БД найдена")
            self._engine.dispose()

    def _get_db(self):
        try:
            self._engine = create_engine(get_sync_database_url())
            with self._engine.connect() as conn:
                pass
            self._engine.dispose()
            return True
        except OperationalError:
            return False
        except Exception as e:
            logger.error(f'При поиске БД возникла ошибка: {e}')
            return False

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

