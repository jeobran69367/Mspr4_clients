"""Event handlers for processing incoming events."""

import json
import logging

from app.events.schemas import OrderCreatedEvent, ProductReservedEvent

logger = logging.getLogger(__name__)


async def handle_order_created(message_body: bytes):
    """Handle order created event."""
    try:
        data = json.loads(message_body.decode())
        event = OrderCreatedEvent(**data)

        logger.info(f"Received order created event: {event.order_id} for customer {event.customer_id}")

        # Process event - e.g., update customer statistics, send notifications, etc.
        # This would typically interact with services to update customer data

    except Exception as e:
        logger.error(f"Error handling order created event: {e}")


async def handle_product_reserved(message_body: bytes):
    """Handle product reserved event."""
    try:
        data = json.loads(message_body.decode())
        event = ProductReservedEvent(**data)

        logger.info(f"Received product reserved event: {event.product_id} for customer {event.customer_id}")

        # Process event - e.g., send notification to customer

    except Exception as e:
        logger.error(f"Error handling product reserved event: {e}")
