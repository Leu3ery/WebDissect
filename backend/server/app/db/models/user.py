from sqlalchemy import Column, Integer, String, DateTime
import datetime

from ._base import Base


class User(Base):
    __tablename__ = "users"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    email         = Column(String(100), nullable=False, unique=True)
    password_hash = Column(String(200), nullable=False)
    created_at    = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)


