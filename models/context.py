from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class CompositionContext(Base):
    __tablename__ = "composition_context"

    id = Column(Integer, primary_key=True, autoincrement=True)
    start_time = Column(DateTime, default=datetime.now(ZoneInfo("Europe/Prague")))
    setting_code = Column(String, default="238")  # openEHR code for 'primary care'
    setting_value = Column(String, default="primary care")  # human-readable
