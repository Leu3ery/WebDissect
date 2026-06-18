from sqlalchemy import Column, Integer, VARCHAR, CheckConstraint, ForeignKey

from ._base import Base


class Endpoint(Base):
    __tablename__ = "endpoints"

    id           = Column(Integer, primary_key=True, autoincrement=True)
    analysis_id  = Column(Integer, ForeignKey("analyses.id"))
    method       = Column(VARCHAR(10), CheckConstraint("method IN ('GET','POST','PUT','PATCH','DELETE','HEAD','OPTIONS')"), nullable=False)
    path         = Column(VARCHAR(200), nullable=False)
    status       = Column(Integer, nullable=False)
    content_type = Column(VARCHAR(100), nullable=False)


