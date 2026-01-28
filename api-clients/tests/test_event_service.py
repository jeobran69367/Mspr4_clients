"""Tests for EventService event creation."""

import uuid
from types import SimpleNamespace

from app.services.event_service import EventService
from app.schemas.event import EventType
from app.models.customer import CustomerType, CustomerStatus


def make_customer(type_is_enum: bool = True, status_is_enum: bool = True):
    """Return a lightweight customer-like object for testing."""
    cid = uuid.uuid4()
    cust_type = CustomerType.PARTICULIER if type_is_enum else CustomerType.PARTICULIER.value
    cust_status = CustomerStatus.EN_ATTENTE if status_is_enum else CustomerStatus.EN_ATTENTE.value

    return SimpleNamespace(
        id=cid,
        reference="REF123",
        email="test@example.com",
        type_client=cust_type,
        statut=cust_status,
        nom="Nom",
        prenom="Prenom",
    )


def test_create_customer_event_with_enums():
    svc = EventService()
    customer = make_customer(type_is_enum=True, status_is_enum=True)

    event = svc.create_customer_event(EventType.CUSTOMER_CREATED, customer)

    assert event.customer_id == customer.id
    assert event.customer_reference == customer.reference
    assert event.customer_email == customer.email
    assert event.customer_type == customer.type_client.value
    assert event.customer_status == customer.statut.value


def test_create_customer_event_with_strings():
    svc = EventService()
    customer = make_customer(type_is_enum=False, status_is_enum=False)

    event = svc.create_customer_event(EventType.CUSTOMER_CREATED, customer)

    assert event.customer_id == customer.id
    assert event.customer_reference == customer.reference
    assert event.customer_email == customer.email
    # When customer fields are strings, event should contain those strings
    assert event.customer_type == customer.type_client
    assert event.customer_status == customer.statut
