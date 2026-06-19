from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from ._base import Base


class ProjectHar(Base):
    __tablename__ = "project_hars"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    har_id     = Column(Integer, ForeignKey("har_files.id"), nullable=False)

    project = relationship("Project", back_populates="hars")
    har     = relationship("HarFile", back_populates="projects")
