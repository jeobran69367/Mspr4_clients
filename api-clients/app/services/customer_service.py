"""Customer service with business logic."""
import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.customer import Customer, CustomerStatus
from app.repositories.customer_repository import CustomerRepository
from app.schemas.customer import CustomerCreate, CustomerUpdate
from app.security.passwords import hash_password


class CustomerService:
    """Customer service with business logic."""

    def __init__(self, db: AsyncSession):
        """Initialize customer service."""
        self.db = db
        self.repository = CustomerRepository(db)

    def _generate_reference(self) -> str:
        """Generate unique customer reference."""
        return f"CLI{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"

    async def create_customer(self, customer_data: CustomerCreate) -> Customer:
        """Create a new customer."""
        # Check if email already exists
        existing = await self.repository.get_by_email(customer_data.email)
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

        # Check if SIRET already exists (for professional customers)
        if customer_data.siret:
            existing_siret = await self.repository.get_by_siret(customer_data.siret)
            if existing_siret:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="SIRET already registered")

        # Create customer
        customer = Customer(
            id=uuid.uuid4(),
            reference=self._generate_reference(),
            civilite=customer_data.civilite,
            nom=customer_data.nom,
            prenom=customer_data.prenom,
            email=customer_data.email,
            telephone=customer_data.telephone,
            mobile=customer_data.mobile,
            type_client=customer_data.type_client,
            raison_sociale=customer_data.raison_sociale,
            siret=customer_data.siret,
            tva_intracommunautaire=customer_data.tva_intracommunautaire,
            nom_contact=customer_data.nom_contact,
            preferences=customer_data.preferences,
            hashed_password=hash_password(customer_data.password),
            statut=CustomerStatus.EN_ATTENTE,
            email_confirme=False,
        )

        return await self.repository.create(customer)

    async def get_customer(self, customer_id: str) -> Optional[Customer]:
        """Get customer by ID."""
        return await self.repository.get_by_id(customer_id)

    async def get_customer_by_email(self, email: str) -> Optional[Customer]:
        """Get customer by email."""
        return await self.repository.get_by_email(email)

    async def update_customer(self, customer_id: str, customer_data: CustomerUpdate) -> Customer:
        """Update customer."""
        customer = await self.repository.get_by_id(customer_id)
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

        # Check email uniqueness if changed
        if customer_data.email and customer_data.email != customer.email:
            existing = await self.repository.get_by_email(customer_data.email)
            if existing:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

        # Check SIRET uniqueness if changed
        if customer_data.siret and customer_data.siret != customer.siret:
            existing_siret = await self.repository.get_by_siret(customer_data.siret)
            if existing_siret:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="SIRET already registered")

        # Update fields
        update_data = customer_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(customer, field, value)

        return await self.repository.update(customer)

    async def delete_customer(self, customer_id: str) -> None:
        """Delete customer (soft delete by changing status)."""
        customer = await self.repository.get_by_id(customer_id)
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

        customer.statut = CustomerStatus.INACTIF
        customer.date_desactivation = datetime.utcnow()
        await self.repository.update(customer)

    async def activate_customer(self, customer_id: str) -> Customer:
        """Activate customer account."""
        customer = await self.repository.get_by_id(customer_id)
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

        customer.statut = CustomerStatus.ACTIF
        customer.email_confirme = True
        return await self.repository.update(customer)

    async def suspend_customer(self, customer_id: str) -> Customer:
        """Suspend customer account."""
        customer = await self.repository.get_by_id(customer_id)
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

        customer.statut = CustomerStatus.SUSPENDU
        return await self.repository.update(customer)

    async def list_customers(self, skip: int = 0, limit: int = 100) -> List[Customer]:
        """List customers with pagination."""
        return await self.repository.get_all(skip=skip, limit=limit)

    async def search_customers(self, query: str, skip: int = 0, limit: int = 100) -> List[Customer]:
        """Search customers."""
        return await self.repository.search(query, skip=skip, limit=limit)

    async def count_customers(self) -> int:
        """Count total customers."""
        return await self.repository.count()
