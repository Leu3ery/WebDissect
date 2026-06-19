from sqlalchemy import Column, Integer, NVARCHAR, CheckConstraint, ForeignKey
from sqlalchemy.orm import relationship

from ._base import Base


class DNSEntry(Base):
    __tablename__ = "dns_entries"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    type       = Column(
        NVARCHAR(4),
        CheckConstraint(
            "type IN ('A','AAAA','MX','NS','TXT','SOA','SRV')",
            name="ck_valid_record_type",
        ),
        nullable=False,
    )
    domain = Column(NVARCHAR(253), nullable=False)
    value  = Column(NVARCHAR(2048), nullable=False)
    ttl    = Column(Integer, CheckConstraint("ttl > 0", name="ck_ttl_greater_zero"), nullable=False)

    project = relationship("Project", back_populates="dns_entries")
