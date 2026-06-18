from sqlalchemy import Column, Integer, String, ForeignKey

from ._base import Base


class HarFile(Base):
    __tablename__ = "har_files"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    filename   = Column(String(30), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)