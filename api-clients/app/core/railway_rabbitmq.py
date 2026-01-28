"""
RabbitMQ client for Railway Production - Service Clients
"""

import os
import json
import logging
import asyncio
import aio_pika
from aio_pika import ExchangeType, Message, DeliveryMode
from typing import Optional
import ssl
from app.core.config import settings

logger = logging.getLogger(__name__)

class ClientsRabbitMQ:
    """RabbitMQ client for Clients service on Railway"""
    
    def __init__(self):
        # Priority: 1. Private URL, 2. Public URL, 3. Constructed
        self.rabbitmq_url = self._get_rabbitmq_url()
        
        self.service_name = settings.SERVICE_NAME
        self.exchange_name = settings.RABBITMQ_EXCHANGE
        
        self.connection: Optional[aio_pika.RobustConnection] = None
        self.channel: Optional[aio_pika.Channel] = None
        
        logger.info(f"🔧 Initializing RabbitMQ for {self.service_name}")
        logger.info(f"📡 URL: {self._mask_url(self.rabbitmq_url)}")
        logger.info(f"📊 Exchange: {self.exchange_name}")
        logger.info(f"🔌 RabbitMQ enabled: {settings.RABBITMQ_ENABLED}")
    
    def _get_rabbitmq_url(self) -> Optional[str]:
        """Get the correct RabbitMQ URL with priority order"""
        # 1. Railway private URL (internal network)
        if settings.RABBITMQ_PRIVATE_URL:
            return settings.RABBITMQ_PRIVATE_URL
        
        # 2. Railway public URL
        if settings.RABBITMQ_URL:
            return settings.RABBITMQ_URL
        
        # 3. Construct from parts (for local development)
        if all([settings.RABBITMQ_HOST, settings.RABBITMQ_USER, settings.RABBITMQ_PASSWORD]):
            return (
                f"amqp://{settings.RABBITMQ_USER}:{settings.RABBITMQ_PASSWORD}"
                f"@{settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}"
                f"/{settings.RABBITMQ_VHOST}"
            )
        
        return None
    
    def _mask_url(self, url: Optional[str]) -> str:
        """Mask password in logs"""
        if not url:
            return "not configured"
        
        if "@" in url:
            parts = url.split("@")
            cred_part = parts[0]
            if ":" in cred_part:
                cred_part = cred_part.split(":")[0] + ":***"
            return f"{cred_part}@{parts[1]}"
        
        return url
    
    def _get_ssl_context(self):
        """Get SSL context if URL uses amqps://"""
        if self.rabbitmq_url and self.rabbitmq_url.startswith("amqps://"):
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            return ssl_context
        return None
    
    async def connect(self) -> bool:
        """Connect to RabbitMQ"""
        if not settings.RABBITMQ_ENABLED:
            logger.warning("⚠️ RabbitMQ is not enabled. Skipping connection.")
            return False
        
        if not self.rabbitmq_url:
            logger.error("❌ No RabbitMQ URL configured")
            return False
        
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                logger.info(f"🔗 Connection attempt {attempt + 1}/{max_retries}")
                
                ssl_context = self._get_ssl_context()
                
                # Railway production connection
                self.connection = await aio_pika.connect_robust(
                    self.rabbitmq_url,
                    ssl_context=ssl_context,
                    timeout=10,
                    heartbeat=30,
                    client_properties={
                        "connection_name": f"{self.service_name}-service",
                        "product": "MSPR-Clients",
                        "platform": "Railway"
                    }
                )
                
                self.channel = await self.connection.channel()
                await self.channel.set_qos(prefetch_count=10)
                
                logger.info("✅ Connected to RabbitMQ")
                return True
                
            except aio_pika.exceptions.AMQPConnectionError as e:
                logger.error(f"❌ AMQP Connection Error: {e}")
                
            except Exception as e:
                logger.error(f"❌ Connection failed: {type(e).__name__}: {e}")
            
            if attempt < max_retries - 1:
                logger.info(f"⏳ Waiting {retry_delay} seconds before retry...")
                await asyncio.sleep(retry_delay)
        
        logger.error("❌ All connection attempts failed")
        return False
    
    async def setup(self):
        """Setup exchange and queue for clients service"""
        if not self.connection:
            logger.error("❌ Not connected to RabbitMQ")
            return False
        
        try:
            # Declare main exchange
            exchange = await self.channel.declare_exchange(
                self.exchange_name,
                ExchangeType.TOPIC,
                durable=True,
                auto_delete=False,
            )
            
            # Clients service queue
            queue_name = settings.RABBITMQ_QUEUE_CLIENTS
            queue = await self.channel.declare_queue(
                queue_name,
                durable=True,
                auto_delete=False,
                arguments={
                    "x-max-length": 10000,
                    "x-message-ttl": 86400000,  # 24 hours
                }
            )
            
            # Bind queue to exchange
            await queue.bind(exchange, routing_key=f"{self.service_name}.#")
            
            # Bind to other services for cross-communication
            await queue.bind(exchange, routing_key="produits.#")
            await queue.bind(exchange, routing_key="commandes.#")
            
            logger.info(f"✅ Setup complete: {queue_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Setup failed: {e}")
            return False
    
    async def publish_client_event(self, event_type: str, data: dict):
        """Publish a client-related event"""
        if not self.connection:
            logger.error("❌ Not connected to RabbitMQ")
            return False
        
        try:
            exchange = await self.channel.get_exchange(self.exchange_name)
            
            routing_key = f"{self.service_name}.{event_type}"
            
            message = Message(
                body=json.dumps(data, ensure_ascii=False).encode('utf-8'),
                delivery_mode=DeliveryMode.PERSISTENT,
                content_type="application/json",
                headers={
                    "source_service": self.service_name,
                    "event_type": event_type,
                    "timestamp": asyncio.get_event_loop().time(),
                }
            )
            
            await exchange.publish(message, routing_key=routing_key)
            
            logger.info(f"📤 Published client event: {routing_key}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Publish failed: {e}")
            return False
    
    async def publish_to_service(self, target_service: str, event_type: str, data: dict):
        """Publish an event to another service"""
        if not self.connection:
            logger.error("❌ Not connected to RabbitMQ")
            return False
        
        try:
            exchange = await self.channel.get_exchange(self.exchange_name)
            
            routing_key = f"{target_service}.{event_type}"
            
            message = Message(
                body=json.dumps(data, ensure_ascii=False).encode('utf-8'),
                delivery_mode=DeliveryMode.PERSISTENT,
                content_type="application/json",
                headers={
                    "source_service": self.service_name,
                    "target_service": target_service,
                    "event_type": event_type,
                }
            )
            
            await exchange.publish(message, routing_key=routing_key)
            
            logger.info(f"📤 Published to {target_service}: {routing_key}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Publish failed: {e}")
            return False
    
    async def start_consumer(self, message_handler):
        """Start consuming messages for clients service"""
        if not self.connection:
            logger.error("❌ Not connected to RabbitMQ")
            return
        
        try:
            queue_name = settings.RABBITMQ_QUEUE_CLIENTS
            queue = await self.channel.get_queue(queue_name)
            
            if not queue:
                logger.error(f"Queue {queue_name} not found")
                return
            
            async def process_message(message):
                async with message.process():
                    try:
                        body = json.loads(message.body.decode('utf-8'))
                        
                        logger.info(f"📩 Received: {message.routing_key}")
                        
                        # Call handler
                        await message_handler(
                            routing_key=message.routing_key,
                            body=body,
                            headers=message.headers or {}
                        )
                        
                    except json.JSONDecodeError:
                        logger.error(f"Invalid JSON in message")
                        await message.nack(requeue=False)
                    except Exception as e:
                        logger.error(f"Error processing message: {e}")
                        await message.nack(requeue=True)
            
            await queue.consume(process_message)
            logger.info(f"📥 Started consuming from {queue_name}")
            
        except Exception as e:
            logger.error(f"❌ Failed to start consumer: {e}")
    
    async def health_check(self) -> dict:
        """Health check for Railway"""
        if not settings.RABBITMQ_ENABLED:
            return {
                "status": "disabled",
                "service": self.service_name,
                "rabbitmq": "not_configured"
            }
        
        if not self.connection or self.connection.is_closed:
            return {
                "status": "disconnected",
                "service": self.service_name,
                "rabbitmq": "not_connected"
            }
        
        try:
            # Test connection by declaring a temporary queue
            test_queue = await self.channel.declare_queue(
                f"health-check-{self.service_name}",
                durable=False,
                auto_delete=True
            )
            await test_queue.delete()
            
            return {
                "status": "healthy",
                "service": self.service_name,
                "rabbitmq": "connected",
                "queue": settings.RABBITMQ_QUEUE_CLIENTS,
                "exchange": self.exchange_name
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "service": self.service_name,
                "rabbitmq": "connection_error",
                "error": str(e)
            }
    
    async def close(self):
        """Close connection gracefully"""
        if self.connection:
            await self.connection.close()
            logger.info("RabbitMQ connection closed")

# Singleton instance
rabbitmq = ClientsRabbitMQ()

#res()
#cgj