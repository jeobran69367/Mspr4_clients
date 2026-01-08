"""RabbitMQ event consumer."""

from typing import Callable, Optional
import ssl

import aio_pika

from app.config import settings


class EventConsumer:
    """RabbitMQ event consumer for receiving events."""

    def __init__(self):
        """Initialize event consumer."""
        self.connection: aio_pika.Connection = None
        self.channel: aio_pika.Channel = None
        self.exchange: aio_pika.Exchange = None

    def _get_rabbitmq_url(self) -> Optional[str]:
        """Get the correct RabbitMQ URL with priority order for Railway."""
        # Priority: 1. Railway private URL, 2. Public URL, 3. Constructed from parts
        if settings.RABBITMQ_PRIVATE_URL:
            return settings.RABBITMQ_PRIVATE_URL
        
        if settings.RABBITMQ_URL:
            return settings.RABBITMQ_URL
        
        # Fallback to constructed URL for local development
        if settings.RABBITMQ_HOST:
            return (
                f"amqp://{settings.RABBITMQ_USER}:{settings.RABBITMQ_PASSWORD}"
                f"@{settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}"
                f"/{settings.RABBITMQ_VHOST}"
            )
        
        return None

    async def connect(self):
        """Connect to RabbitMQ."""
        rabbitmq_url = self._get_rabbitmq_url()
        
        if not rabbitmq_url:
            return  # Skip connection if RabbitMQ is not configured
        
        if self.connection is None or self.connection.is_closed:
            # Check if SSL is needed (amqps://)
            ssl_context = None
            if rabbitmq_url.startswith("amqps://"):
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
            
            self.connection = await aio_pika.connect_robust(
                rabbitmq_url,
                ssl_context=ssl_context,
            )
            self.channel = await self.connection.channel()
            await self.channel.set_qos(prefetch_count=10)

            # Declare exchange
            self.exchange = await self.channel.declare_exchange(
                "payetonkawa.events", aio_pika.ExchangeType.TOPIC, durable=True
            )

    async def close(self):
        """Close RabbitMQ connection."""
        if self.channel:
            await self.channel.close()
        if self.connection:
            await self.connection.close()

    async def consume(self, queue_name: str, routing_keys: list, callback: Callable):
        """Start consuming messages from a queue."""
        await self.connect()

        # Declare queue
        queue = await self.channel.declare_queue(queue_name, durable=True)

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
