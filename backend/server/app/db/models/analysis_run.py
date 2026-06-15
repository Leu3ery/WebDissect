import datetime

from sqlalchemy import Column, Integer, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship

from ._base import Base


class AnalysisRun(Base):
    __tablename__ = "analysis_runs"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    kind       = Column(Text, nullable=False, default="analysis")  # analysis|ports|paths
    summary    = Column(Text, nullable=False, default="{}")        # JSON: per-category counts
    snapshot   = Column(Text, nullable=False, default="{}")        # JSON: full ProjectFull

    project = relationship("Project", back_populates="analysis_runs")
