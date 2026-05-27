from sqlalchemy import Column, Integer, VARCHAR

from ._base import Base


class Technology(Base):
    __tablename__ = "technologies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR(100), nullable=False)
    description = Column(VARCHAR(100), nullable=False)
    icon_url = Column(VARCHAR(100), nullable=False)


