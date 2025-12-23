"""Events package initialization."""
from app.events.producer import event_producer, EventProducer
from app.events.consumer import event_consumer, EventConsumer
from app.events.handlers import handle_order_created, handle_product_reserved

__all__ = [
    "event_producer",
    "EventProducer",
    "event_consumer",
    "EventConsumer",
    "handle_order_created",
    "handle_product_reserved",
]
