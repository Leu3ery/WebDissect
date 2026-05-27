from sqlalchemy import Column, Integer, VARCHAR, CheckConstraint

from ._base import Base


class Endpoint(Base):
    __tablename__ = "endpoints"

    id           = Column(Integer, primary_key=True, autoincrement=True)
    method       = Column(VARCHAR(10), CheckConstraint("method IN (GET,POST,PUT,DELETE)"), nullable=False)
    path         = Column(VARCHAR(200), nullable=False)
    status       = Column(Integer, CheckConstraint("100 < status & status < 600"), nullable=False)
    content_type = Column(VARCHAR(100), nullable=False)


