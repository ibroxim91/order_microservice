import os
import json
import asyncio
import aio_pika
from celery import Celery
import time

# Celery config — Redis broker & backend
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
CELERY_BACKEND_URL = os.getenv("CELERY_BACKEND_URL", "redis://redis:6379/1")
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
QUEUE_NAME = "orders.new_order"
EXCHANGE_NAME = "orders"
ROUTING_KEY = "new_order"


celery_app = Celery("orders", broker=CELERY_BROKER_URL, backend=CELERY_BACKEND_URL)


@celery_app.task(name="orders.process_order_task") 
def process_order_task(order_id: str): 
    time.sleep(2) 
    print(f"Order {order_id} processed")
    return True



async def consume():
    # Retry logic: Waiting for RabbitMQ to be ready
    for attempt in range(10):
        try:
            connection = await aio_pika.connect_robust(RABBITMQ_URL)
            print("✅ Connected to RabbitMQ")
            break
        except Exception as e:
            print(f"❌ RabbitMQ not ready, retrying... attempt {attempt+1}/10")
            await asyncio.sleep(5)
    else:
        raise RuntimeError("RabbitMQ connection failed after 10 retries")

    async with connection:
        channel = await connection.channel()
        exchange = await channel.declare_exchange(EXCHANGE_NAME, aio_pika.ExchangeType.TOPIC, durable=True)
        queue = await channel.declare_queue(QUEUE_NAME, durable=True)
        await queue.bind(exchange, ROUTING_KEY)

        async with queue.iterator() as qiter:
            async for message in qiter:
                async with message.process():
                    data = json.loads(message.body.decode())
                    order_id = data.get("order_id")
                    print(f"📦 New order received: {order_id}")
                    celery_app.send_task("orders.process_order_task", args=[order_id])
                    # or: process_order_task.delay(order_id)


if __name__ == "__main__":
    asyncio.run(consume())
