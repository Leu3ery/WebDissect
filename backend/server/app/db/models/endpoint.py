from sqlalchemy import Column, Integer, VARCHAR, CheckConstraint, ForeignKey
from sqlalchemy.orm import relationship

from ._base import Base


class Endpoint(Base):
    __tablename__ = "endpoints"

    id           = Column(Integer, primary_key=True, autoincrement=True)
    project_id   = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    method       = Column(VARCHAR(10), nullable=False)
    path         = Column(VARCHAR(2048), nullable=False)
    status       = Column(
        Integer,
        CheckConstraint("status > 100 AND status < 600", name="ck_status_range"),
        nullable=False,
    )
    content_type = Column(VARCHAR(100), nullable=False)

    project = relationship("Project", back_populates="endpoints")
