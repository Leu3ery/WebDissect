import datetime

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

from ._base import Base


class User(Base):
    __tablename__ = "users"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    email         = Column(String(100), nullable=False, unique=True, index=True)
    # Nullable: an account created via OTP login may not have a password yet.
    password_hash = Column(String(200), nullable=True)
    created_at    = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)

    projects = relationship(
        "Project", back_populates="user", cascade="all, delete-orphan"
    )
