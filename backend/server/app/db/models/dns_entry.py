from sqlalchemy import Column, Integer, NVARCHAR, CheckConstraint

from ._base import Base


class DNSEntry(Base):
    __tablename__ = "dns_entries"

    id     = Column(Integer, primary_key=True, autoincrement=True)
    type   = Column(NVARCHAR(4), CheckConstraint("type IN (A,AAAA,MX,NS,TXT)", name="ck_valid_record_type"), nullable=False)
    domain = Column(NVARCHAR(253), nullable=False)
    value  = Column(NVARCHAR(253), nullable=False)
    ttl    = Column(Integer, CheckConstraint("ttl > 0", name="ck_ttl_greater_zero"), nullable=False)

