"""RabbitMQ event producer - Railway Production Ready."""

import os
import json
import logging
import ssl
from typing import Optional

import aio_pika
from aio_pika import ExchangeType, Message, DeliveryMode

from app.config import settings
from app.schemas.event import AddressEvent, CustomerEvent

logger = logging.getLogger(__name__)


class RailwayRabbitMQ:
    """RabbitMQ client for Railway PRODUCTION."""

    def __init__(self):
        # 1. PRIORITÉ: URL privée Railway
        self.rabbitmq_url = os.getenv("RABBITMQ_PRIVATE_URL")

        # 2. Fallback: URL publique Railway
        if not self.rabbitmq_url:
            self.rabbitmq_url = os.getenv("RABBITMQ_URL")

        # 3. Fallback: Construire à partir des variables d'environnement
        if not self.rabbitmq_url:
            host = os.getenv("RABBITMQ_HOST", "rabbitmq")
            port = os.getenv("RABBITMQ_PORT", "5672")
            username = os.getenv("RABBITMQ_USER", "guest")
            password = os.getenv("RABBITMQ_PASSWORD", "guest")
            vhost = os.getenv("RABBITMQ_VHOST", "/")

            self.rabbitmq_url = f"amqp://{username}:{password}@{host}:{port}/{vhost}"

        self.service_name = os.getenv("SERVICE_NAME", "clients")
        self.exchange_name = os.getenv("RABBITMQ_EXCHANGE", "mspr.events")

        self.connection: Optional[aio_pika.RobustConnection] = None
        self.channel: Optional[aio_pika.Channel] = None
        self.exchange: Optional[aio_pika.Exchange] = None

        logger.info(f"🔧 Initializing RabbitMQ for {self.service_name}")
        logger.info(f"📡 URL: {self._mask_url(self.rabbitmq_url)}")
        logger.info(f"🏷️  Service: {self.service_name}")
        logger.info(f"📊 Exchange: {self.exchange_name}")

    def _mask_url(self, url: str) -> str:
        """Mask password in logs."""
        if url and "@" in url:
            parts = url.split("@")
            cred_part = parts[0]
            if ":" in cred_part:
                protocol_user = cred_part.rsplit(":", 1)[0]
                return f"{protocol_user}:****@{parts[1]}"
        return url

    async def connect(self):
        """Connect to RabbitMQ with SSL support for amqps."""
        if self.connection and not self.connection.is_closed:
            logger.info("✅ Already connected to RabbitMQ")
            return

        try:
            # SSL context for amqps://
            ssl_context = None
            if self.rabbitmq_url.startswith("amqps://"):
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
                logger.info("🔐 Using SSL/TLS connection")

            # Connect with robust connection (auto-reconnect)
            self.connection = await aio_pika.connect_robust(
                self.rabbitmq_url,
                ssl_context=ssl_context,
            )

            self.channel = await self.connection.channel()
            logger.info("📡 Connected to RabbitMQ successfully")

            # Declare exchange (idempotent)
            self.exchange = await self.channel.declare_exchange(
                self.exchange_name,
                ExchangeType.TOPIC,
                durable=True,
            )
            logger.info(f"📊 Exchange '{self.exchange_name}' ready")

            # Declare queue for this service
            queue_name = f"{self.service_name}.queue"
            queue = await self.channel.declare_queue(
                queue_name,
                durable=True,
            )
            logger.info(f"📥 Queue '{queue_name}' declared")

            # Bind queue to exchange with routing keys
            routing_keys = [
                f"{self.service_name}.*",  # clients.*
                "customer.*",  # customer events
                "address.*",  # address events
            ]

            for routing_key in routing_keys:
                await queue.bind(self.exchange, routing_key=routing_key)
                logger.info(f"🔗 Bound queue to routing key: {routing_key}")

        except Exception as e:
            logger.error(f"❌ Failed to connect to RabbitMQ: {e}")
            raise

    async def close(self):
        """Close RabbitMQ connection."""
        try:
            if self.channel:
                await self.channel.close()
            if self.connection:
                await self.connection.close()
            logger.info("🔌 RabbitMQ connection closed")
        except Exception as e:
            logger.error(f"Error closing RabbitMQ: {e}")

    async def publish(self, routing_key: str, message_data: dict):
        """Publish a message to the exchange."""
        if not settings.RABBITMQ_ENABLED:
            logger.debug("RabbitMQ not enabled, skipping publish")
            return

        try:
            await self.connect()

            if not self.exchange:
                logger.warning("Exchange not available, skipping publish")
                return

            message_body = json.dumps(message_data).encode()

            message = Message(
                body=message_body,
                delivery_mode=DeliveryMode.PERSISTENT,
                content_type="application/json",
            )

            await self.exchange.publish(message, routing_key=routing_key)
            logger.info(f"📤 Published message to {routing_key}")

        except Exception as e:
            logger.error(f"❌ Failed to publish message: {e}")
            raise

    async def publish_customer_event(self, event: CustomerEvent):
        """Publish a customer event."""
        try:
            routing_key = f"customer.{event.metadata.event_type.value.split('.')[1]}"
            message_data = json.loads(event.model_dump_json())
            await self.publish(routing_key, message_data)
        except Exception as e:
            logger.error(f"Failed to publish customer event: {e}")

    async def publish_address_event(self, event: AddressEvent):
        """Publish an address event."""
        try:
            routing_key = f"address.{event.metadata.event_type.value.split('.')[1]}"
            message_data = json.loads(event.model_dump_json())
            await self.publish(routing_key, message_data)
        except Exception as e:
            logger.error(f"Failed to publish address event: {e}")


# Global event producer instance
event_producer = RailwayRabbitMQ()
