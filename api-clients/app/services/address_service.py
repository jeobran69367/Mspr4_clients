"""Address service with business logic."""
from typing import List, Optional
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.models.address import Address
from app.repositories.address_repository import AddressRepository
from app.schemas.address import AddressCreate, AddressUpdate


class AddressService:
    """Address service with business logic."""

    def __init__(self, db: AsyncSession):
        """Initialize address service."""
        self.db = db
        self.repository = AddressRepository(db)

    async def create_address(self, customer_id: str, address_data: AddressCreate) -> Address:
        """Create a new address for a customer."""
        # If this is set as default, unset other defaults
        if address_data.est_defaut:
            addresses = await self.repository.get_by_customer_id(customer_id)
            for addr in addresses:
                if addr.est_defaut:
                    addr.est_defaut = False

        address = Address(
            id=uuid.uuid4(),
            client_id=customer_id,
            type_adresse=address_data.type_adresse,
            est_defaut=address_data.est_defaut,
            libelle=address_data.libelle,
            destinataire=address_data.destinataire,
            adresse_ligne1=address_data.adresse_ligne1,
            adresse_ligne2=address_data.adresse_ligne2,
            code_postal=address_data.code_postal,
            ville=address_data.ville,
            pays=address_data.pays,
            instructions_livraison=address_data.instructions_livraison,
            telephone=address_data.telephone,
        )

        return await self.repository.create(address)

    async def get_address(self, address_id: str) -> Optional[Address]:
        """Get address by ID."""
        return await self.repository.get_by_id(address_id)

    async def get_customer_addresses(self, customer_id: str) -> List[Address]:
        """Get all addresses for a customer."""
        return await self.repository.get_by_customer_id(customer_id)

    async def get_default_address(self, customer_id: str) -> Optional[Address]:
        """Get default address for a customer."""
        return await self.repository.get_default_address(customer_id)

    async def update_address(self, address_id: str, address_data: AddressUpdate) -> Address:
        """Update an address."""
        address = await self.repository.get_by_id(address_id)
        if not address:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")

        # If setting as default, unset other defaults
        if address_data.est_defaut is True and not address.est_defaut:
            await self.repository.set_default_address(address_id, address.client_id)

        # Update fields
        update_data = address_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(address, field, value)

        return await self.repository.update(address)

    async def delete_address(self, address_id: str) -> None:
        """Delete an address."""
        address = await self.repository.get_by_id(address_id)
        if not address:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")

        await self.repository.delete(address)

    async def set_as_default(self, address_id: str, customer_id: str) -> Address:
        """Set an address as default."""
        address = await self.repository.get_by_id(address_id)
        if not address:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")

        if str(address.client_id) != customer_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Address does not belong to this customer")

        await self.repository.set_default_address(address_id, customer_id)
        return await self.repository.get_by_id(address_id)
