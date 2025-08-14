from sqlalchemy_utils import database_exists, database_exists, create_database
from sqlalchemy.orm import sessionmaker
from db_connect import ReminderDB
from db_models import Base

reminder = ReminderDB()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=reminder.get_engine())

class CreateDB:
    def __init__(self):
        if not database_exists(reminder.get_database_url):
            create_database(reminder.get_database_url)
        else:
            print("База создана ранее")

class CreateTable:
    def __init__(self):
        if not database_exists(reminder.get_database_url):
            print("База данных не найдена")
        else:
            Base.metadata.create_all(reminder.get_engine())

class RecordAdd:
    pass

class RecordUpdate:
    pass

class RecordDelete:
    pass


