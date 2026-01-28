"""Integration test: create a customer then listen for RabbitMQ event `customer.created`.

Usage:
  python integration_create_customer_and_listen.py

Environment variables (optional):
  CLIENTS_API_URL - default http://localhost:8000
  RABBITMQ_URL - default amqp://guest:guest@localhost:5672/
  RABBITMQ_EXCHANGE - default mspr.events
  EVENT_TIMEOUT - seconds to wait for the event (default 8)

Dependencies:
  pip install httpx aio-pika
"""

import asyncio
import os
import json
import httpx
import aio_pika

API_URL = os.getenv("CLIENTS_API_URL", "http://localhost:8000")
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
EXCHANGE = os.getenv("RABBITMQ_EXCHANGE", "mspr.events")
EXPECTED_ROUTING_KEY = os.getenv("EXPECTED_ROUTING_KEY", "customer.created")
TIMEOUT = int(os.getenv("EVENT_TIMEOUT", "8"))


async def listen_for_event(expected_routing_key=EXPECTED_ROUTING_KEY, timeout=TIMEOUT):
    conn = await aio_pika.connect_robust(RABBITMQ_URL)
    channel = await conn.channel()
    exchange = await channel.declare_exchange(EXCHANGE, aio_pika.ExchangeType.TOPIC, durable=True)

    # Temporary exclusive queue
    q = await channel.declare_queue(exclusive=True)
    await q.bind(exchange, routing_key=expected_routing_key)

    try:
        async with q.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    body = json.loads(message.body.decode())
                    print("Received event:", json.dumps(body, indent=2, ensure_ascii=False))
                    await conn.close()
                    return body
    except Exception as e:
        await conn.close()
        print("Listener error:", e)
        return None


async def main():
    # 1) Create a customer
    payload = {
        "nom": "Dupont",
        "prenom": "Jean",
        "email": f"jean.dupont.test+{int(asyncio.get_event_loop().time())}@example.com",
        "password": "supersecret123",
    }

    async with httpx.AsyncClient() as client:
        r = await client.post(f"{API_URL}/api/v1/customers/", json=payload, timeout=15)
        print("Create customer status:", r.status_code)
        print(r.text)
        if r.status_code != 201:
            return

    # 2) Listen for event (with a timeout wrapper)
    try:
        event = await asyncio.wait_for(listen_for_event(), timeout=TIMEOUT)
    except asyncio.TimeoutError:
        event = None

    if event:
        print("Event OK")
    else:
        print("No event received within timeout")


if __name__ == "__main__":
    asyncio.run(main())
