from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import Column, DateTime, Float, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class PulseOximetry(Base):
    __tablename__ = "pulse_oximetry"

    id = Column(Integer, primary_key=True, autoincrement=True)
    spo2_numerator = Column(Float, nullable=False)
    spo2_denominator = Column(Float, nullable=False, default=100.0)
    timestamp = Column(DateTime, default=datetime.now(ZoneInfo("Europe/Prague")))
