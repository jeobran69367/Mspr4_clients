"""RabbitMQ event consumer - Railway Production Ready."""

import os
import logging
import ssl
from typing import Callable, Optional

import aio_pika
from aio_pika import ExchangeType

from app.config import settings

logger = logging.getLogger(__name__)


class RabbitMQConsumer:
    """RabbitMQ consumer for Railway PRODUCTION."""

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

        logger.info(f"🔧 Initializing RabbitMQ Consumer for {self.service_name}")

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
            await self.channel.set_qos(prefetch_count=10)
            logger.info("📡 Consumer connected to RabbitMQ successfully")

            # Declare exchange (idempotent)
            self.exchange = await self.channel.declare_exchange(
                self.exchange_name,
                ExchangeType.TOPIC,
                durable=True,
            )
            logger.info(f"📊 Exchange '{self.exchange_name}' ready for consumer")

        except Exception as e:
            logger.error(f"❌ Failed to connect consumer to RabbitMQ: {e}")
            raise

    async def close(self):
        """Close RabbitMQ connection."""
        try:
            if self.channel:
                await self.channel.close()
            if self.connection:
                await self.connection.close()
            logger.info("🔌 RabbitMQ consumer connection closed")
        except Exception as e:
            logger.error(f"Error closing RabbitMQ consumer: {e}")

    async def consume(self, queue_name: str, routing_keys: list, callback: Callable):
        """Start consuming messages from a queue."""
        if not settings.RABBITMQ_ENABLED:
            logger.info("RabbitMQ not enabled, skipping consumer")
            return

        try:
            await self.connect()

            # Declare queue
            queue = await self.channel.declare_queue(queue_name, durable=True)
            logger.info(f"📥 Queue '{queue_name}' declared for consumer")

            # Bind queue to exchange with routing keys
            for routing_key in routing_keys:
                await queue.bind(self.exchange, routing_key=routing_key)
                logger.info(f"🔗 Consumer bound queue to routing key: {routing_key}")

            # Start consuming
            logger.info(f"👂 Starting to consume messages from '{queue_name}'")
            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    async with message.process():
                        await callback(message.body)

        except Exception as e:
            logger.error(f"❌ Error in consumer: {e}")
            raise


# Global event consumer instance
event_consumer = RabbitMQConsumer()
