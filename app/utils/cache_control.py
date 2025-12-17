import json
from typing import Optional
from app.config import REDIS_CLIENT as redis
from app.schemas.order_schema import OrderCreate, OrderUpdateStatus, OrderOut
CACHE_TTL = 300  # 5 minut


# Cache’dan order olish
async def get_order_from_cache(order_id: str) -> Optional[dict]:
    data = await redis.get(f"order:{order_id}")
    if data:
        data = json.loads(data)
        return OrderOut(**data)
    return None


# Cache’ga order yozish
async def set_order_to_cache(order_id: str, order_data: dict) -> None:
    await redis.set(f"order:{order_id}", json.dumps(order_data), ex=CACHE_TTL)


# Cache’dagi orderni yangilash
async def update_order_cache(order_id: str, order_data: dict) -> None:
    await set_order_to_cache(order_id, order_data)


# Cache’dan orderni o‘chirish (agar kerak bo‘lsa)
async def delete_order_cache(order_id: str) -> None:
    await redis.delete(f"order:{order_id}")
