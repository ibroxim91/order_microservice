import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, Any

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, String, Float, DateTime, Enum as SqlEnum, JSON
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from app.models.base import Base


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    SHIPPED = "SHIPPED"
    CANCELED = "CANCELED"


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    items: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    total_price: Mapped[float] = mapped_column(Float, nullable=False)

    status: Mapped[OrderStatus] = mapped_column(SqlEnum(OrderStatus), default=OrderStatus.PENDING)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
