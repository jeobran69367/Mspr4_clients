"""Events package initialization."""

from app.events.consumer import RabbitMQConsumer, event_consumer
from app.events.handlers import handle_order_created, handle_product_reserved
from app.events.producer import RailwayRabbitMQ, event_producer

__all__ = [
    "event_producer",
    "RailwayRabbitMQ",
    "event_consumer",
    "RabbitMQConsumer",
    "handle_order_created",
    "handle_product_reserved",
]
