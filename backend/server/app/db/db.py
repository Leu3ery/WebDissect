import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.models._base import Base
from app.config import get_settings

# Import models so they are registered on the Base metadata before create_all.
from app.db import models  # noqa: F401


_settings = get_settings()
os.makedirs(_settings.DB_DIR, exist_ok=True)
_db_path = os.path.join(_settings.DB_DIR, _settings.DB_FILENAME)

engine = create_engine(
    f"sqlite:///{_db_path}",
    pool_pre_ping=True,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    Base.metadata.create_all(engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
