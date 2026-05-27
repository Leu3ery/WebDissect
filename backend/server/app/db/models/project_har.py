from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from ._base import Base


class ProjectHar(Base):
    __tablename__ = "project_hars"

    project_id = Column(Integer, ForeignKey("projects.id"))
    har_id = Column(Integer, ForeignKey("har_files.id"))

    project = relationship("Project", back_populates="projecthar")
    har = relationship("HarFile", back_populates="projecthar")

