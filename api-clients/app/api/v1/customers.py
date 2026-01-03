"""Customer API endpoints."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dependencies import get_current_active_user, require_admin
from app.services.customer_service import CustomerService
from app.services.event_service import EventService
from app.schemas.customer import (
    CustomerCreate,
    CustomerUpdate,
    CustomerResponse,
    CustomerWithAddresses,
    CustomerListResponse,
)
from app.schemas.event import EventType
from app.events.producer import event_producer
from app.models.customer import Customer

router = APIRouter(prefix="/customers", tags=["customers"])


@router.post("/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(
    customer_data: CustomerCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new customer."""
    service = CustomerService(db)
    customer = await service.create_customer(customer_data)

    # Publish event
    event_service = EventService()
    event = event_service.create_customer_event(EventType.CUSTOMER_CREATED, customer)
    await event_producer.publish_customer_event(event)

    return customer


@router.get("/me", response_model=CustomerWithAddresses)
async def get_current_customer(
    current_user: Customer = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current authenticated customer with addresses."""
    service = CustomerService(db)
    customer = await service.get_customer(str(current_user.id))
    return customer


@router.get("/{customer_id}", response_model=CustomerWithAddresses)
async def get_customer(
    customer_id: str,
    current_user: Customer = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get customer by ID (own data or admin only)."""
    # Check if user is accessing their own data or is admin
    if str(current_user.id) != customer_id and current_user.type_client != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    service = CustomerService(db)
    customer = await service.get_customer(customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    return customer


@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: str,
    customer_data: CustomerUpdate,
    current_user: Customer = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update customer (own data or admin only)."""
    # Check if user is updating their own data or is admin
    if str(current_user.id) != customer_id and current_user.type_client != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    service = CustomerService(db)
    customer = await service.update_customer(customer_id, customer_data)

    # Publish event
    event_service = EventService()
    event = event_service.create_customer_event(EventType.CUSTOMER_UPDATED, customer)
    await event_producer.publish_customer_event(event)

    return customer


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(
    customer_id: str,
    current_user: Customer = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete customer (admin only)."""
    if current_user.type_client != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    service = CustomerService(db)
    customer = await service.get_customer(customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )

    await service.delete_customer(customer_id)

    # Publish event
    event_service = EventService()
    event = event_service.create_customer_event(EventType.CUSTOMER_DELETED, customer)
    await event_producer.publish_customer_event(event)


@router.get("/", response_model=CustomerListResponse)
async def list_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: Optional[str] = None,
    current_user: Customer = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """List all customers (admin only)."""
    service = CustomerService(db)

    if search:
        customers = await service.search_customers(search, skip=skip, limit=limit)
    else:
        customers = await service.list_customers(skip=skip, limit=limit)

    total = await service.count_customers()
    pages = (total + limit - 1) // limit

    return CustomerListResponse(
        items=customers,
        total=total,
        page=skip // limit + 1,
        page_size=limit,
        pages=pages
    )
