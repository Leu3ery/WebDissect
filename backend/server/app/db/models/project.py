from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from ._base import Base


class Project(Base):
    __tablename__ = "projects"

    id      = Column(Integer, primary_key=True, autoincrement=True)
    name    = Column(String(30), nullable=False)
    domain  = Column(String(253), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    user = relationship("User", back_populates="projects")

    certificates = relationship(
        "Certificate", back_populates="project", cascade="all, delete-orphan"
    )
    dns_entries = relationship(
        "DNSEntry", back_populates="project", cascade="all, delete-orphan"
    )
    technologies = relationship(
        "Technology", back_populates="project", cascade="all, delete-orphan"
    )
    endpoints = relationship(
        "Endpoint", back_populates="project", cascade="all, delete-orphan"
    )
    subdomains = relationship(
        "Subdomain", back_populates="project", cascade="all, delete-orphan"
    )
    ports = relationship(
        "Port", back_populates="project", cascade="all, delete-orphan"
    )
    path_entries = relationship(
        "PathEntry", back_populates="project", cascade="all, delete-orphan"
    )
    hars = relationship(
        "ProjectHar", back_populates="project", cascade="all, delete-orphan"
    )
