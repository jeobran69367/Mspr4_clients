"""Event schemas for RabbitMQ messaging."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel


class EventType(str, Enum):
    """Event type enumeration."""

    CUSTOMER_CREATED = "customer.created"
    CUSTOMER_UPDATED = "customer.updated"
    CUSTOMER_DELETED = "customer.deleted"
    CUSTOMER_STATUS_CHANGED = "customer.status_changed"
    ADDRESS_CREATED = "address.created"
    ADDRESS_UPDATED = "address.updated"
    ADDRESS_DELETED = "address.deleted"


class EventMetadata(BaseModel):
    """Event metadata."""

    event_id: UUID
    event_type: EventType
    timestamp: datetime
    source_service: str = "api-clients"
    correlation_id: Optional[str] = None


class CustomerEvent(BaseModel):
    """Customer event schema."""

    metadata: EventMetadata
    customer_id: UUID
    customer_reference: str
    customer_email: str
    customer_type: str
    customer_status: str
    data: Optional[Dict[str, Any]] = None


class AddressEvent(BaseModel):
    """Address event schema."""

    metadata: EventMetadata
    address_id: UUID
    customer_id: UUID
    address_type: str
    data: Optional[Dict[str, Any]] = None
