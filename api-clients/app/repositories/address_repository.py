"""Address repository."""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.address import Address, AddressType
from app.repositories.base_repository import BaseRepository


class AddressRepository(BaseRepository[Address]):
    """Address repository with specific queries."""

    def __init__(self, db: AsyncSession):
        """Initialize address repository."""
        super().__init__(Address, db)

    async def get_by_customer_id(self, customer_id: str) -> List[Address]:
        """Get all addresses for a customer."""
        result = await self.db.execute(
            select(Address).where(Address.client_id == customer_id)
        )
        return list(result.scalars().all())

    async def get_default_address(self, customer_id: str) -> Optional[Address]:
        """Get default address for a customer."""
        result = await self.db.execute(
            select(Address)
            .where(Address.client_id == customer_id)
            .where(Address.est_defaut.is_(True))
        )
        return result.scalar_one_or_none()

    async def get_by_type(
        self,
        customer_id: str,
        address_type: AddressType
    ) -> List[Address]:
        """Get addresses by type for a customer."""
        result = await self.db.execute(
            select(Address)
            .where(Address.client_id == customer_id)
            .where(Address.type_adresse == address_type)
        )
        return list(result.scalars().all())

    async def set_default_address(self, address_id: str, customer_id: str) -> None:
        """Set an address as default and unset others."""
        # Unset all default addresses for this customer
        addresses = await self.get_by_customer_id(customer_id)
        for addr in addresses:
            if addr.est_defaut:
                addr.est_defaut = False

        # Set the new default address
        address = await self.get_by_id(address_id)
        if address:
            address.est_defaut = True

        await self.db.commit()
