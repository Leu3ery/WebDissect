from sqlalchemy import Column, Integer, ForeignKey, Boolean

from ._base import Base



class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    is_dns_analysis_completed = Column(Boolean, default=False)
    is_cert_analysis_completed = Column(Boolean, default=False)

