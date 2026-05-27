from sqlalchemy import Column, Integer, String, DateTime

from ._base import Base


class PendingVerification(Base):
    __tablename__ = "pending_verifications"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    email      = Column(String(100), nullable=False, unique=True)
    code       = Column(String(6), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    attempts   = Column(Integer, nullable=False, default=0)


