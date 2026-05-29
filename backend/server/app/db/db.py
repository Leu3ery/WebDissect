from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.models._base import Base
from app.config import get_settings


engine = create_engine("sqlite:////app/db/" + get_settings().DB_FILENAME, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    Base.metadata.create_all(engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()