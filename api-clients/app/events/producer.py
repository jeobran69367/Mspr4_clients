"""RabbitMQ event producer."""

from typing import Optional
import ssl

import aio_pika
from aio_pika import DeliveryMode, Message

from app.config import settings
from app.schemas.event import AddressEvent, CustomerEvent


class EventProducer:
    """RabbitMQ event producer for publishing events."""

    def __init__(self):
        """Initialize event producer."""
        self.connection: Optional[aio_pika.Connection] = None
        self.channel: Optional[aio_pika.Channel] = None
        self.exchange: Optional[aio_pika.Exchange] = None

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

    async def publish_customer_event(self, event: CustomerEvent):
        """Publish a customer event."""
        if not settings.RABBITMQ_ENABLED:
            return  # Skip publishing if RabbitMQ is not configured

        await self.connect()

        if not self.exchange:
            return  # Skip if connection failed

        message = Message(
            body=event.model_dump_json().encode(),
            delivery_mode=DeliveryMode.PERSISTENT,
            content_type="application/json",
        )

        routing_key = f"customer.{event.metadata.event_type.value.split('.')[1]}"
        await self.exchange.publish(message, routing_key=routing_key)

    async def publish_address_event(self, event: AddressEvent):
        """Publish an address event."""
        if not settings.RABBITMQ_ENABLED:
            return  # Skip publishing if RabbitMQ is not configured

        await self.connect()

        if not self.exchange:
            return  # Skip if connection failed

        message = Message(
            body=event.model_dump_json().encode(),
            delivery_mode=DeliveryMode.PERSISTENT,
            content_type="application/json",
        )

        routing_key = f"address.{event.metadata.event_type.value.split('.')[1]}"
        await self.exchange.publish(message, routing_key=routing_key)


# Global event producer instance
event_producer = EventProducer()
