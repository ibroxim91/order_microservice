from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from uuid import UUID
from app.models.order import Order, OrderStatus

class OrderCRUD:
    @staticmethod
    async def create(db: AsyncSession, user_id: int, items: dict, total_price: float) -> Order:
        order = Order(user_id=user_id, items=items, total_price=total_price)
        db.add(order)
        await db.commit()
        await db.refresh(order)
        return order

    @staticmethod
    async def get(db: AsyncSession, order_id: UUID) -> Optional[Order]:
        res = await db.execute(select(Order).where(Order.id == order_id))
        return res.scalar_one_or_none()

    @staticmethod
    async def update_status(db: AsyncSession, order_id: UUID, status: OrderStatus) -> Optional[Order]:
        order = await OrderCRUD.get(db, order_id)
        if not order:
            return None
        order.status = status
        await db.commit()
        await db.refresh(order)
        return order

    @staticmethod
    async def list_by_user(db: AsyncSession, user_id: int) -> List[Order]:
        res = await db.execute(select(Order).where(Order.user_id == user_id).order_by(Order.created_at.desc()))
        return res.scalars().all()
