"""RabbitMQ event consumer."""
from typing import Callable
import aio_pika
from app.config import settings


class EventConsumer:
    """RabbitMQ event consumer for receiving events."""

    def __init__(self):
        """Initialize event consumer."""
        self.connection: aio_pika.Connection = None
        self.channel: aio_pika.Channel = None
        self.exchange: aio_pika.Exchange = None

    async def connect(self):
        """Connect to RabbitMQ."""
        if self.connection is None or self.connection.is_closed:
            self.connection = await aio_pika.connect_robust(
                host=settings.RABBITMQ_HOST,
                port=settings.RABBITMQ_PORT,
                login=settings.RABBITMQ_USER,
                password=settings.RABBITMQ_PASSWORD,
                virtualhost=settings.RABBITMQ_VHOST,
            )
            self.channel = await self.connection.channel()
            await self.channel.set_qos(prefetch_count=10)

            # Declare exchange
            self.exchange = await self.channel.declare_exchange(
                "payetonkawa.events",
                aio_pika.ExchangeType.TOPIC,
                durable=True
            )

    async def close(self):
        """Close RabbitMQ connection."""
        if self.channel:
            await self.channel.close()
        if self.connection:
            await self.connection.close()

    async def consume(
        self,
        queue_name: str,
        routing_keys: list,
        callback: Callable
    ):
        """Start consuming messages from a queue."""
        await self.connect()

        # Declare queue
        queue = await self.channel.declare_queue(
            queue_name,
            durable=True
        )

        # Bind queue to exchange with routing keys
        for routing_key in routing_keys:
            await queue.bind(self.exchange, routing_key=routing_key)

        # Start consuming
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    await callback(message.body)


# Global event consumer instance
event_consumer = EventConsumer()
