from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship

from ._base import Base



class Analysis(Base):
    __tablename__ = "analyses"

    id                         = Column(Integer, primary_key=True)
    project_id                 = Column(Integer, ForeignKey("projects.id"))
    started_at                 = Column(DateTime, default=datetime.now)
    is_dns_analysis_completed  = Column(Boolean, default=False)  # TODO: remove
    is_cert_analysis_completed = Column(Boolean, default=False)  # TODO: remove

    project = relationship("Project", back_populates="analyses")