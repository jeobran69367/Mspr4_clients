"""Customer repository."""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func
from app.models.customer import Customer, CustomerStatus, CustomerType
from app.repositories.base_repository import BaseRepository


class CustomerRepository(BaseRepository[Customer]):
    """Customer repository with specific queries."""

    def __init__(self, db: AsyncSession):
        """Initialize customer repository."""
        super().__init__(Customer, db)

    async def get_by_email(self, email: str) -> Optional[Customer]:
        """Get customer by email."""
        result = await self.db.execute(
            select(Customer).where(Customer.email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_reference(self, reference: str) -> Optional[Customer]:
        """Get customer by reference."""
        result = await self.db.execute(
            select(Customer).where(Customer.reference == reference)
        )
        return result.scalar_one_or_none()

    async def get_by_siret(self, siret: str) -> Optional[Customer]:
        """Get customer by SIRET."""
        result = await self.db.execute(
            select(Customer).where(Customer.siret == siret)
        )
        return result.scalar_one_or_none()

    async def search(
        self,
        query: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Customer]:
        """Search customers by name, email, or reference."""
        search_term = f"%{query}%"
        result = await self.db.execute(
            select(Customer).where(
                or_(
                    Customer.nom.ilike(search_term),
                    Customer.prenom.ilike(search_term),
                    Customer.email.ilike(search_term),
                    Customer.reference.ilike(search_term),
                    Customer.raison_sociale.ilike(search_term),
                )
            ).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_type(
        self,
        customer_type: CustomerType,
        skip: int = 0,
        limit: int = 100
    ) -> List[Customer]:
        """Get customers by type."""
        result = await self.db.execute(
            select(Customer)
            .where(Customer.type_client == customer_type)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_status(
        self,
        status: CustomerStatus,
        skip: int = 0,
        limit: int = 100
    ) -> List[Customer]:
        """Get customers by status."""
        result = await self.db.execute(
            select(Customer)
            .where(Customer.statut == status)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_by_type(self, customer_type: CustomerType) -> int:
        """Count customers by type."""
        result = await self.db.execute(
            select(func.count()).select_from(Customer).where(Customer.type_client == customer_type)
        )
        return result.scalar_one()

    async def count_by_status(self, status: CustomerStatus) -> int:
        """Count customers by status."""
        result = await self.db.execute(
            select(func.count()).select_from(Customer).where(Customer.statut == status)
        )
        return result.scalar_one()
