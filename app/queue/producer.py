import os
import json
import aio_pika

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
EXCHANGE_NAME = "orders"
ROUTING_KEY = "new_order"

async def publish_new_order(order_id: str, user_id: int):
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    async with connection:
        channel = await connection.channel()
        exchange = await channel.declare_exchange(EXCHANGE_NAME, aio_pika.ExchangeType.TOPIC, durable=True)
        message_body = json.dumps({"order_id": order_id, "user_id": user_id}).encode()
        await exchange.publish(
            aio_pika.Message(body=message_body),
            routing_key=ROUTING_KEY
        )
        print(f"📤 Published new_order event for order {order_id}")
