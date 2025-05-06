from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.ehr_models import Base

DATABASE_URL = "sqlite:///./ehr.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite specifické
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)
