"""Admin API endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dependencies import require_admin
from app.services.customer_service import CustomerService
from app.services.event_service import EventService
from app.schemas.customer import CustomerResponse
from app.schemas.event import EventType
from app.events.producer import event_producer
from app.models.customer import Customer

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/customers/{customer_id}/activate", response_model=CustomerResponse)
async def activate_customer(
    customer_id: str,
    current_user: Customer = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Activate a customer account."""
    service = CustomerService(db)
    customer = await service.activate_customer(customer_id)

    # Publish event
    event_service = EventService()
    event = event_service.create_customer_event(EventType.CUSTOMER_STATUS_CHANGED, customer)
    await event_producer.publish_customer_event(event)

    return customer


@router.post("/customers/{customer_id}/suspend", response_model=CustomerResponse)
async def suspend_customer(
    customer_id: str,
    current_user: Customer = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Suspend a customer account."""
    service = CustomerService(db)
    customer = await service.suspend_customer(customer_id)

    # Publish event
    event_service = EventService()
    event = event_service.create_customer_event(EventType.CUSTOMER_STATUS_CHANGED, customer)
    await event_producer.publish_customer_event(event)

    return customer


@router.get("/stats")
async def get_stats(
    current_user: Customer = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get customer statistics."""
    from app.repositories.customer_repository import CustomerRepository
    from app.models.customer import CustomerType, CustomerStatus

    repo = CustomerRepository(db)

    stats = {
        "total_customers": await repo.count(),
        "by_type": {
            "particulier": await repo.count_by_type(CustomerType.PARTICULIER),
            "professionnel": await repo.count_by_type(CustomerType.PROFESSIONNEL),
            "distributeur": await repo.count_by_type(CustomerType.DISTRIBUTEUR),
            "admin": await repo.count_by_type(CustomerType.ADMIN),
        },
        "by_status": {
            "actif": await repo.count_by_status(CustomerStatus.ACTIF),
            "inactif": await repo.count_by_status(CustomerStatus.INACTIF),
            "suspendu": await repo.count_by_status(CustomerStatus.SUSPENDU),
            "en_attente": await repo.count_by_status(CustomerStatus.EN_ATTENTE),
        }
    }

    return stats
