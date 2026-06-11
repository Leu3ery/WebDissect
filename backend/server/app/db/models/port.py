from sqlalchemy import Column, Integer, VARCHAR, ForeignKey
from sqlalchemy.orm import relationship

from ._base import Base


class Port(Base):
    __tablename__ = "ports"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    port       = Column(Integer, nullable=False)
    protocol   = Column(VARCHAR(4), nullable=False, default="tcp")
    state      = Column(VARCHAR(10), nullable=False, default="open")
    service    = Column(VARCHAR(40), nullable=False, default="")
    version    = Column(VARCHAR(120), nullable=False, default="")
    banner     = Column(VARCHAR(500), nullable=False, default="")

    project = relationship("Project", back_populates="ports")
