"""RabbitMQ event producer."""
import json
from typing import Optional
import aio_pika
from aio_pika import Message, DeliveryMode
from app.config import settings
from app.schemas.event import CustomerEvent, AddressEvent


class EventProducer:
    """RabbitMQ event producer for publishing events."""
    
    def __init__(self):
        """Initialize event producer."""
        self.connection: Optional[aio_pika.Connection] = None
        self.channel: Optional[aio_pika.Channel] = None
        self.exchange: Optional[aio_pika.Exchange] = None
    
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
    
    async def publish_customer_event(self, event: CustomerEvent):
        """Publish a customer event."""
        await self.connect()
        
        message = Message(
            body=event.model_dump_json().encode(),
            delivery_mode=DeliveryMode.PERSISTENT,
            content_type="application/json",
        )
        
        routing_key = f"customer.{event.metadata.event_type.value.split('.')[1]}"
        await self.exchange.publish(message, routing_key=routing_key)
    
    async def publish_address_event(self, event: AddressEvent):
        """Publish an address event."""
        await self.connect()
        
        message = Message(
            body=event.model_dump_json().encode(),
            delivery_mode=DeliveryMode.PERSISTENT,
            content_type="application/json",
        )
        
        routing_key = f"address.{event.metadata.event_type.value.split('.')[1]}"
        await self.exchange.publish(message, routing_key=routing_key)


# Global event producer instance
event_producer = EventProducer()
