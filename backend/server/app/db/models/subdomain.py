from sqlalchemy import Column, Integer, NVARCHAR, ForeignKey
from sqlalchemy.orm import relationship

from ._base import Base


class Subdomain(Base):
    __tablename__ = "subdomains"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    name       = Column(NVARCHAR(253), nullable=False)
    ip         = Column(NVARCHAR(45))
    source     = Column(NVARCHAR(20), nullable=False, default="crt.sh")

    project = relationship("Project", back_populates="subdomains")
