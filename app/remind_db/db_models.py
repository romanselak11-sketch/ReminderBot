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


class ReminderDate(Base):
    __tablename__ = 'reminder_date'

    tg_user_id = Column(BigInteger, index=True)
    reminder_message = Column(String, index=True)
    reminder_date = Column(DateTime, index=True, nullable=True)
    time_zone = Column(Integer, index=True)
    reminder_id = Column(String, index=True, primary_key=True)


class ReminderInterval(Base):
    __tablename__ = 'reminder_intervals'

    tg_user_id = Column(BigInteger, index=True)
    reminder_message = Column(String, index=True)
    reminder_id = Column(String, index=True, primary_key=True)
    interval = Column(String, index=True)


class ReminderTrigger(Base):
    __tablename__ = 'reminder_triggers'

    tg_user_id = Column(BigInteger, index=True)
    reminder_message = Column(String, index=True)
    time_zone = Column(Integer, index=True)
    reminder_id = Column(String, index=True, primary_key=True)
    year = Column(Integer, index=True)
    month = Column(Integer, index=True)
    day = Column(Integer, index=True)
    weekday = Column(Integer, index=True)
    day_of_week = Column(String, index=True)
    hour = Column(Integer, index=True)
    minute = Column(Integer, index=True)
    second = Column(Integer, index=True)



