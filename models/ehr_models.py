from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


def now_prague():
    return datetime.now(ZoneInfo("Europe/Prague"))


# ---------------------------- MODELY ----------------------------


class Patient(Base):
    __tablename__ = "patient"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    birth_date = Column(DateTime, nullable=True)

    ehr = relationship("EHR", back_populates="patient", uselist=False)


class EHR(Base):
    __tablename__ = "ehr"

    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patient.id"))
    created_at = Column(DateTime, default=now_prague)

    patient = relationship("Patient", back_populates="ehr")
    compositions = relationship("Composition", back_populates="ehr")


class CompositionContext(Base):
    __tablename__ = "composition_context"

    id = Column(Integer, primary_key=True, autoincrement=True)
    start_time = Column(DateTime, default=now_prague)
    setting_code = Column(String, default="238")
    setting_value = Column(String, default="primary care")


class Composition(Base):
    __tablename__ = "composition"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ehr_id = Column(Integer, ForeignKey("ehr.id"))
    context_id = Column(Integer, ForeignKey("composition_context.id"))
    name = Column(String, nullable=False, default="Clinical document")
    start_time = Column(DateTime, default=now_prague)
    composer = Column(String, nullable=True)
    setting = Column(String, nullable=True)

    ehr = relationship("EHR", back_populates="compositions")
    context = relationship("CompositionContext")

    pulse = relationship("Pulse", back_populates="composition")
    blood_pressure = relationship("BloodPressure", back_populates="composition")
    body_temperature = relationship("BodyTemperature", back_populates="composition")
    respiration = relationship("Respiration", back_populates="composition")
    pulse_oximetry = relationship("PulseOximetry", back_populates="composition")


class PulseOximetry(Base):
    __tablename__ = "pulse_oximetry"

    id = Column(Integer, primary_key=True, autoincrement=True)
    composition_id = Column(Integer, ForeignKey("composition.id"))
    spo2_numerator = Column(Float, nullable=False)
    spo2_denominator = Column(Float, nullable=False, default=100.0)
    timestamp = Column(DateTime, default=now_prague)

    composition = relationship("Composition", back_populates="pulse_oximetry")


class Respiration(Base):
    __tablename__ = "respiration"

    id = Column(Integer, primary_key=True, autoincrement=True)
    composition_id = Column(Integer, ForeignKey("composition.id"))
    rate = Column(Float, nullable=True)
    rate_unit = Column(String, default="/min")
    timestamp = Column(DateTime, default=now_prague)

    composition = relationship("Composition", back_populates="respiration")


class BodyTemperature(Base):
    __tablename__ = "body_temperature"

    id = Column(Integer, primary_key=True, autoincrement=True)
    composition_id = Column(Integer, ForeignKey("composition.id"))
    temperature = Column(Float, nullable=False)
    unit = Column(String, default="Cel")
    body_exposure = Column(String, nullable=True)
    location = Column(String, nullable=True)
    timestamp = Column(DateTime, default=now_prague)

    composition = relationship("Composition", back_populates="body_temperature")


class BloodPressure(Base):
    __tablename__ = "blood_pressure"

    id = Column(Integer, primary_key=True, autoincrement=True)
    composition_id = Column(Integer, ForeignKey("composition.id"))
    systolic = Column(Float, nullable=True)
    diastolic = Column(Float, nullable=True)
    position = Column(String, nullable=True)
    location = Column(String, nullable=True)
    timestamp = Column(DateTime, default=now_prague)

    composition = relationship("Composition", back_populates="blood_pressure")


class Pulse(Base):
    __tablename__ = "pulse"

    id = Column(Integer, primary_key=True, autoincrement=True)
    composition_id = Column(Integer, ForeignKey("composition.id"))
    rate = Column(Float, nullable=True)
    rate_unit = Column(String, default="/min")
    position = Column(String, nullable=True)
    body_site = Column(String, nullable=True)
    timestamp = Column(DateTime, default=now_prague)

    composition = relationship("Composition", back_populates="pulse")
