from sqlalchemy import Column, Integer, VARCHAR, ForeignKey
from sqlalchemy.orm import relationship

from ._base import Base


class Technology(Base):
    __tablename__ = "technologies"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    project_id  = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    name        = Column(VARCHAR(100), nullable=False)
    description = Column(VARCHAR(255), nullable=False, default="")
    icon_url    = Column(VARCHAR(255), nullable=False, default="")

    project = relationship("Project", back_populates="technologies")
