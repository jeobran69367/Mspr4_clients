"""Event schemas for RabbitMQ messages."""
from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime
from uuid import UUID


class BaseEvent(BaseModel):
    """Base event schema."""

    event_id: UUID
    event_type: str
    timestamp: datetime
    source_service: str
    correlation_id: str = None


class OrderCreatedEvent(BaseEvent):
    """Order created event from Orders service."""

    order_id: UUID
    customer_id: UUID
    total_amount: float
    data: Dict[str, Any] = None


class ProductReservedEvent(BaseEvent):
    """Product reserved event from Products service."""

    product_id: UUID
    customer_id: UUID
    quantity: int
    data: Dict[str, Any] = None
