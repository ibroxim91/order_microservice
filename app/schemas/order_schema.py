from pydantic import BaseModel
from typing import Dict, Any
from uuid import UUID
from datetime import datetime
from enum import Enum

class OrderStatus(str, Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    SHIPPED = "SHIPPED"
    CANCELED = "CANCELED"

class OrderCreate(BaseModel):
    items: Dict[str, Any]
    total_price: float

class OrderUpdateStatus(BaseModel):
    status: OrderStatus

class OrderOut(BaseModel):
    id: UUID
    user_id: int
    items: Dict[str, Any]
    total_price: float
    status: OrderStatus
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True
