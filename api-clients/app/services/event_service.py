"""Event service for RabbitMQ messaging."""

import uuid
from datetime import datetime
from typing import Optional

from app.models.address import Address
from app.models.customer import Customer
from app.schemas.event import AddressEvent, CustomerEvent, EventMetadata, EventType


class EventService:
    """Event service for creating and managing events."""

    def __init__(self):
        """Initialize event service."""
        pass

    def create_customer_event(
        self, event_type: EventType, customer: Customer, correlation_id: Optional[str] = None
    ) -> CustomerEvent:
        """Create a customer event."""
        metadata = EventMetadata(
            event_id=uuid.uuid4(),
            event_type=event_type,
            timestamp=datetime.utcnow(),
            source_service="api-clients",
            correlation_id=correlation_id,
        )

        event = CustomerEvent(
            metadata=metadata,
            customer_id=customer.id,
            customer_reference=customer.reference,
            customer_email=customer.email,
            customer_type=customer.type_client.value,
            customer_status=customer.statut.value,
            data={
                "nom": customer.nom,
                "prenom": customer.prenom,
                "type_client": customer.type_client.value,
                "statut": customer.statut.value,
            },
        )

        return event

    def create_address_event(
        self, event_type: EventType, address: Address, customer_id: uuid.UUID, correlation_id: Optional[str] = None
    ) -> AddressEvent:
        """Create an address event."""
        metadata = EventMetadata(
            event_id=uuid.uuid4(),
            event_type=event_type,
            timestamp=datetime.utcnow(),
            source_service="api-clients",
            correlation_id=correlation_id,
        )

        event = AddressEvent(
            metadata=metadata,
            address_id=address.id,
            customer_id=customer_id,
            address_type=address.type_adresse.value,
            data={
                "ville": address.ville,
                "code_postal": address.code_postal,
                "pays": address.pays,
                "est_defaut": address.est_defaut,
            },
        )

        return event
