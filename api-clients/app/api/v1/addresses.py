"""Address API endpoints."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_active_user
from app.events.producer import event_producer
from app.models.customer import Customer
from app.schemas.address import AddressCreate, AddressResponse, AddressUpdate
from app.schemas.event import EventType
from app.services.address_service import AddressService
from app.services.event_service import EventService

router = APIRouter(prefix="/addresses", tags=["addresses"])


@router.post("/", response_model=AddressResponse, status_code=status.HTTP_201_CREATED)
async def create_address(
    address_data: AddressCreate, current_user: Customer = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)
):
    """Create a new address for current customer."""
    service = AddressService(db)
    address = await service.create_address(str(current_user.id), address_data)

    # Publish event
    event_service = EventService()
    event = event_service.create_address_event(EventType.ADDRESS_CREATED, address, current_user.id)
    await event_producer.publish_address_event(event)

    return address


@router.get("/", response_model=List[AddressResponse])
async def list_addresses(current_user: Customer = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)):
    """List all addresses for current customer."""
    service = AddressService(db)
    addresses = await service.get_customer_addresses(str(current_user.id))
    return addresses


@router.get("/default", response_model=AddressResponse)
async def get_default_address(current_user: Customer = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)):
    """Get default address for current customer."""
    service = AddressService(db)
    address = await service.get_default_address(str(current_user.id))
    if not address:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No default address found")
    return address


@router.get("/{address_id}", response_model=AddressResponse)
async def get_address(
    address_id: str, current_user: Customer = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)
):
    """Get address by ID."""
    service = AddressService(db)
    address = await service.get_address(address_id)
    if not address:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")

    # Check if address belongs to current user
    if str(address.client_id) != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    return address


@router.put("/{address_id}", response_model=AddressResponse)
async def update_address(
    address_id: str,
    address_data: AddressUpdate,
    current_user: Customer = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Update address."""
    service = AddressService(db)
    address = await service.get_address(address_id)
    if not address:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")

    # Check if address belongs to current user
    if str(address.client_id) != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    address = await service.update_address(address_id, address_data)

    # Publish event
    event_service = EventService()
    event = event_service.create_address_event(EventType.ADDRESS_UPDATED, address, current_user.id)
    await event_producer.publish_address_event(event)

    return address


@router.delete("/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_address(
    address_id: str, current_user: Customer = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)
):
    """Delete address."""
    service = AddressService(db)
    address = await service.get_address(address_id)
    if not address:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")

    # Check if address belongs to current user
    if str(address.client_id) != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    # Publish event before deletion
    event_service = EventService()
    event = event_service.create_address_event(EventType.ADDRESS_DELETED, address, current_user.id)

    await service.delete_address(address_id)
    await event_producer.publish_address_event(event)


@router.post("/{address_id}/set-default", response_model=AddressResponse)
async def set_default_address(
    address_id: str, current_user: Customer = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)
):
    """Set address as default."""
    service = AddressService(db)
    address = await service.set_as_default(address_id, str(current_user.id))

    # Publish event
    event_service = EventService()
    event = event_service.create_address_event(EventType.ADDRESS_UPDATED, address, current_user.id)
    await event_producer.publish_address_event(event)

    return address
