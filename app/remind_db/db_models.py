from sqlalchemy import Column, Integer, DateTime, BigInteger, String
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime


Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tg_user_id = Column(BigInteger, primary_key=True, index=True)
    time_zone = Column(Integer, index=True)
    created_at = Column(DateTime, default=datetime.now, index=True)


class Reminder(Base):
    __tablename__ = 'reminders'

    tg_user_id = Column(BigInteger, primary_key=True, index=True)
    reminder_message = Column(String, index=True)
    reminder_date = Column(DateTime, index=True)
    time_zone = Column(Integer, index=True)



