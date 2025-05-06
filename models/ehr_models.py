# Tento soubor obsahuje SQLAlchemy modely odpovídající jednotlivým archetypům podle tvého Web Template.

from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import Column, DateTime, Float, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


def now_prague():
    return datetime.now(ZoneInfo("Europe/Prague"))


class CompositionContext(Base):
    __tablename__ = "composition_context"

    id = Column(Integer, primary_key=True, autoincrement=True)
    start_time = Column(DateTime, default=now_prague)
    setting_code = Column(String, default="238")
    setting_value = Column(String, default="primary care")


class PulseOximetry(Base):
    __tablename__ = "pulse_oximetry"

    id = Column(Integer, primary_key=True, autoincrement=True)
    spo2_numerator = Column(Float, nullable=False)
    spo2_denominator = Column(Float, nullable=False, default=100.0)
    timestamp = Column(DateTime, default=now_prague)


class Respiration(Base):
    __tablename__ = "respiration"

    id = Column(Integer, primary_key=True, autoincrement=True)
    rate = Column(Float, nullable=True)
    rate_unit = Column(String, default="/min")
    timestamp = Column(DateTime, default=now_prague)


class BodyTemperature(Base):
    __tablename__ = "body_temperature"

    id = Column(Integer, primary_key=True, autoincrement=True)
    temperature = Column(Float, nullable=False)
    unit = Column(String, default="Cel")
    body_exposure = Column(
        String, nullable=True
    )  # Např. "Naked", "Appropriate clothing/bedding"
    location = Column(String, nullable=True)  # Např. "Forehead", "Mouth"
    timestamp = Column(DateTime, default=now_prague)


class BloodPressure(Base):
    __tablename__ = "blood_pressure"

    id = Column(Integer, primary_key=True, autoincrement=True)
    systolic = Column(Float, nullable=True)
    diastolic = Column(Float, nullable=True)
    position = Column(String, nullable=True)
    location = Column(String, nullable=True)
    timestamp = Column(DateTime, default=now_prague)


class Pulse(Base):
    __tablename__ = "pulse"

    id = Column(Integer, primary_key=True, autoincrement=True)
    rate = Column(Float, nullable=True)
    rate_unit = Column(String, default="/min")
    position = Column(String, nullable=True)
    body_site = Column(String, nullable=True)
    timestamp = Column(DateTime, default=now_prague)
