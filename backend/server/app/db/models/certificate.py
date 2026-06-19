from sqlalchemy import Column, Integer, NVARCHAR, CHAR, DateTime, VARCHAR, ForeignKey
from sqlalchemy.orm import relationship

from ._base import Base


class Certificate(Base):
    __tablename__ = "certificates"

    id                   = Column(Integer,       primary_key=True, autoincrement=True)
    project_id           = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    subject_domain       = Column(NVARCHAR(253), nullable=False)
    subject_organization = Column(NVARCHAR(64))
    subject_country      = Column(CHAR(2))
    issuer_name          = Column(NVARCHAR(253), nullable=False)
    issuer_organization  = Column(NVARCHAR(64))
    issuer_country       = Column(CHAR(2))
    valid_from           = Column(DateTime,      nullable=False)
    valid_to             = Column(DateTime,      nullable=False)
    serial_number        = Column(VARCHAR(40),   nullable=False)
    public_key_type      = Column(VARCHAR(10),   nullable=False)
    fingerprint_sha256   = Column(CHAR(64),      nullable=False)

    project = relationship("Project", back_populates="certificates")
