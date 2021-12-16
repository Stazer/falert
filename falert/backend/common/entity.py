from uuid import UUID, uuid4
from typing import List

from sqlalchemy import Column, DateTime, Float, Text, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import declarative_base, relationship

BaseEntity = declarative_base()


class ForestEntity(BaseEntity):
    __tablename__ = "forests"

    id: UUID = Column(PGUUID(as_uuid=False), primary_key=True, default=uuid4)

    name = Column(Text)

    vertices: List[ForestVertexEntity] = relationship(
        "ForestVertexEntity",
        back_populates="forest",
    )

    created = Column(DateTime, server_default=func.now(), nullable=False)
    updated = Column(DateTime, onupdate=func.now(), nullable=False)


class ForestVertexEntity(BaseEntity):
    __tablename__ = "forest_vertices"

    id: UUID = Column(PGUUID(as_uuid=False), primary_key=True, default=uuid4)

    forest_id: UUID = Column(PGUUID(as_uuid=False), ForeignKey("forest.id"))
    forest: ForestEntity = relationship(
        "ForestEntity",
        back_populates="vertices",
    )

    latitude: float = Column(Float)
    longitude: float = Column(Float)
