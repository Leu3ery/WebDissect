from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from ._base import Base


class HarFile(Base):
    __tablename__ = "har_files"

    id       = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(255), nullable=False)

    projects = relationship(
        "ProjectHar", back_populates="har", cascade="all, delete-orphan"
    )
