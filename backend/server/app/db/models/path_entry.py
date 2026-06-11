from sqlalchemy import Column, Integer, VARCHAR, ForeignKey
from sqlalchemy.orm import relationship

from ._base import Base


class PathEntry(Base):
    __tablename__ = "path_entries"

    id           = Column(Integer, primary_key=True, autoincrement=True)
    project_id   = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    path         = Column(VARCHAR(2048), nullable=False)
    status       = Column(Integer, nullable=False)
    content_type = Column(VARCHAR(100), nullable=False, default="")
    length       = Column(Integer, nullable=False, default=0)

    project = relationship("Project", back_populates="path_entries")
