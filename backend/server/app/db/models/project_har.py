from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from ._base import Base


class ProjectHar(Base):
    __tablename__ = "project_hars"

    project_id = Column(Integer, ForeignKey("projects.id"), primary_key=True)
    har_id     = Column(Integer, ForeignKey("har_files.id"), primary_key=True)

    project = relationship("Project", back_populates="project_hars")
    har     = relationship("HarFile", back_populates="project")

