from sqlalchemy import Column, Integer, String, DateTime, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime


Base = declarative_base()

class Reminder(Base):
    __tablename__ = 'reminders'

    id = Column(Integer, primary_key=True, index=True)
    tg_user_id = Column(BigInteger, nullable=False, index=True)
    text = Column(String(200), index=True)
    date = Column(DateTime, nullable=False, index=True)
    chat_id = Column(BigInteger, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.now, index=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, index=True)
