from sqlalchemy import Column, Integer, NVARCHAR, CHAR, DateTime, VARCHAR

from ._base import Base

class Certificate(Base):
    __tablename__ = "certificates"

    id                   = Column(Integer,       primary_key=True, autoincrement=True)
    subject_domain       = Column(NVARCHAR(253), nullable=False)
    subject_organization = Column(NVARCHAR(64),  nullable=True)
    subject_country      = Column(CHAR(2))
    issuer_name          = Column(NVARCHAR(253), nullable=False)
    issuer_organization  = Column(NVARCHAR(64))
    issuer_country       = Column(CHAR(2))
    valid_from           = Column(DateTime,      nullable=False)
    valid_to             = Column(DateTime,      nullable=False)
    serial_number        = Column(VARCHAR(40),   nullable=False)
    public_key_type      = Column(VARCHAR(10),   nullable=False)
    fingerprint_sha256   = Column(CHAR(64),      nullable=False, unique=True)
