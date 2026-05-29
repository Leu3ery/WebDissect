from sqlalchemy import Column, Integer, String

from ._base import Base


class HarFile(Base):
    __tablename__ = "har_files"

    id       = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(30), nullable=False)


