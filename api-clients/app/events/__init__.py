"""Events package initialization."""

from app.events.consumer import EventConsumer, event_consumer
from app.events.handlers import handle_order_created, handle_product_reserved
from app.events.producer import EventProducer, event_producer

__all__ = [
    "event_producer",
    "EventProducer",
    "event_consumer",
    "EventConsumer",
    "handle_order_created",
    "handle_product_reserved",
]
