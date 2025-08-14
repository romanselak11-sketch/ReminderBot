import os
import logging

from dotenv import load_dotenv
from sqlalchemy import create_engine, Engine
from typing import Optional
from urllib.parse import quote_plus


class ReminderDB:
    def __init__(self):
        load_dotenv()
        self._engine: Optional[Engine] = None
        self._database_url: Optional[Engine] = None

    def _config_database_url(self):
        subd = self._get_env("SUBD")
        username = self._get_env("USERNAME")
        password = quote_plus(self._get_env("PASSWORD"))
        host = self._get_env("HOST")
        port = self._get_env("PORT")
        name = self._get_env("DB_NAME")

        return f"{subd}://{username}:{password}@{host}:{port}/{name}"

    def _get_env(self, key):
        value = os.getenv(key)
        if value is None:
            print(f"Для ключа {key} значение не установлено")
        return value


    @property
    def get_database_url(self):
        if self._database_url is None:
            self._database_url = self._config_database_url()
        return self._database_url


    def get_engine(self):
        if self._engine is None:
            self._engine = create_engine(self.get_database_url)
        return self._engine





