from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from ._base import Base


class Project(Base):
    __tablename__ = "projects"

    id      = Column(Integer, primary_key=True, autoincrement=True)
    name    = Column(String(30), nullable=False)
    domain  = Column(String(253), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    user         = relationship("User", back_populates="projects")
    project_hars = relationship("HarFile", back_populates="project")
    analyses     = relationship("Analysis", back_populates="project")
