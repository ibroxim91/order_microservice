import os
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.schemas.order_schema import OrderCreate, OrderUpdateStatus, OrderOut
from app.crud.order_crud import OrderCRUD
from app.auth.get_user import get_current_user 
from app.queue.producer import publish_new_order
from app.utils.cache_control import get_order_from_cache, set_order_to_cache
from app.utils.get_remote_ip import get_remote_address
from slowapi import Limiter 
from dotenv import load_dotenv
load_dotenv()

POST_LIMIT = os.getenv("POST_LIMIT", "10/minute")
PATCH_LIMIT = os.getenv("PATCH_LIMIT", "10/minute")
GET_LIMIT = os.getenv("GET_LIMIT", "10/minute")


limiter = Limiter(key_func=get_remote_address)
order_router = APIRouter()

@order_router.post("/", response_model=OrderOut)
@limiter.limit(POST_LIMIT)
async def create_order( request: Request, payload: OrderCreate, db: AsyncSession = Depends(get_db), user: int = Depends(get_current_user)):
    order = await OrderCRUD.create(db, user_id=user.id, items=payload.items, total_price=payload.total_price)
    await publish_new_order(str(order.id), order.user_id)
    return order


@order_router.get("/{order_id}/", response_model=OrderOut)
@limiter.limit(GET_LIMIT)
async def get_order(request: Request, order_id: UUID, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    # Avval cache’dan tekshir
    cached = await get_order_from_cache(str(order_id))
    if cached :
        return cached

    # Agar cache’da yo‘q bo‘lsa → DB’dan olib cache’ga yoz
    order = await OrderCRUD.get(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order_data = OrderOut.from_orm(order).dict()
    order_data["id"] = str(order_data["id"])
    order_data["created_at"] = str(order_data["created_at"])
    await set_order_to_cache(str(order.id), order_data)
    return order_data


@order_router.patch("/{order_id}/", response_model=OrderOut)
@limiter.limit(PATCH_LIMIT)
async def update_order_status( request: Request,order_id: UUID, payload: OrderUpdateStatus, db: AsyncSession = Depends(get_db), user: int = Depends(get_current_user)):
    order = await OrderCRUD.update_status(db, order_id, payload.status)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    order_data = OrderOut.from_orm(order).dict()
    order_data["id"] = str(order_data["id"])
    order_data["created_at"] = str(order_data["created_at"])
    await set_order_to_cache(str(order.id), order_data)    
    return order

@order_router.get("/user/{user_id}/", response_model=List[OrderOut])
@limiter.limit(GET_LIMIT)
async def get_user_orders(request: Request, user_id: int, db: AsyncSession = Depends(get_db), user: int = Depends(get_current_user)):
    orders = await OrderCRUD.list_by_user(db, user_id)
    return orders
