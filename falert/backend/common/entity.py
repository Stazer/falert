from typing import List, Any
import uuid

from sqlalchemy import Column, DateTime, Float, Text, ForeignKey, func
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.types import TypeDecorator, CHAR


class UUID(TypeDecorator):
    impl = CHAR

    def __init__(self, **_kwargs) -> None:
        super().__init__()

    def load_dialect_impl(self, dialect: Any) -> Any:
        if dialect.name == "postgresql":
            return dialect.type_descriptor(postgresql.UUID())

        return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value: Any, dialect: Any) -> Any:
        if value is None:
            return value

        if dialect.name == "postgresql":
            return str(value)

        if not isinstance(value, uuid.UUID):
            value = uuid.UUID(value)

        return value.hex

    def process_result_value(self, value: Any, dialect: Any) -> Any:
        if value is None:
            return value

        if not isinstance(value, uuid.UUID):
            value = uuid.UUID(value)

        return value

    def process_literal_param(self, value: Any, dialect: Any):
        raise NotImplementedError()

    @property
    def python_type(self) -> Any:
        raise NotImplementedError()


BaseEntity = declarative_base()


class SubscriptionEntity(BaseEntity):
    __tablename__ = "subscriptions"

    id: UUID = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)

    vertices: List["SubscriptionVertexEntity"] = relationship(
        "SubscriptionVertexEntity",
        back_populates="subscription",
    )

    created = Column(DateTime, server_default=func.now(), nullable=False)
    updated = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )


class SubscriptionVertexEntity(BaseEntity):
    __tablename__ = "subscription_vertices"

    id: UUID = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)

    subscription_id: UUID = Column(UUID(as_uuid=False), ForeignKey("subscriptions.id"))
    subscription: "SubscriptionEntity" = relationship(
        "SubscriptionEntity",
        back_populates="vertices",
    )

    latitude: float = Column(Float)
    longitude: float = Column(Float)
