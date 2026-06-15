from sqlalchemy import Column, Integer, VARCHAR, ForeignKey
from sqlalchemy.orm import relationship

from ._base import Base


class SecurityCheck(Base):
    __tablename__ = "security_checks"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    category   = Column(VARCHAR(20), nullable=False)   # header | tls | cookie
    name       = Column(VARCHAR(80), nullable=False)
    status     = Column(VARCHAR(10), nullable=False)   # ok | warn | fail | info
    severity   = Column(VARCHAR(10), nullable=False, default="info")  # high|medium|low|info
    detail     = Column(VARCHAR(500), nullable=False, default="")

    project = relationship("Project", back_populates="security_checks")
