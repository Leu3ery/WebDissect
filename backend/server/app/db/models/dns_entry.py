from sqlalchemy import Column, Integer, NVARCHAR, CheckConstraint, ForeignKey

from ._base import Base


class DNSEntry(Base):
    __tablename__ = "dns_entries"

    id     = Column(Integer, primary_key=True, autoincrement=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"))
    type   = Column(
        NVARCHAR(5),
        CheckConstraint("type IN ('A','AAAA','MX','NS','TXT','CNAME','SRV','SOA')", name="ck_valid_record_type"),
        nullable=False
    )
    domain = Column(NVARCHAR(253), nullable=False)
    value  = Column(NVARCHAR(253), nullable=False)
    ttl    = Column(Integer, CheckConstraint("ttl > 0", name="ck_ttl_greater_zero"), nullable=False)

