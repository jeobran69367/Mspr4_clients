"""Address schemas for API validation."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.models.address import AddressType


class AddressBase(BaseModel):
    """Base address schema."""
    type_adresse: AddressType
    est_defaut: bool = False
    libelle: Optional[str] = None
    destinataire: Optional[str] = None
    adresse_ligne1: str = Field(..., min_length=1, max_length=255)
    adresse_ligne2: Optional[str] = None
    code_postal: str = Field(..., min_length=1, max_length=10)
    ville: str = Field(..., min_length=1, max_length=100)
    pays: str = Field(default="France", max_length=100)
    instructions_livraison: Optional[str] = None
    telephone: Optional[str] = None


class AddressCreate(AddressBase):
    """Schema for creating an address."""
    pass


class AddressUpdate(BaseModel):
    """Schema for updating an address."""
    type_adresse: Optional[AddressType] = None
    est_defaut: Optional[bool] = None
    libelle: Optional[str] = None
    destinataire: Optional[str] = None
    adresse_ligne1: Optional[str] = Field(None, min_length=1, max_length=255)
    adresse_ligne2: Optional[str] = None
    code_postal: Optional[str] = Field(None, min_length=1, max_length=10)
    ville: Optional[str] = Field(None, min_length=1, max_length=100)
    pays: Optional[str] = Field(None, max_length=100)
    instructions_livraison: Optional[str] = None
    telephone: Optional[str] = None


class AddressResponse(AddressBase):
    """Schema for address response."""
    id: UUID
    client_id: UUID
    date_creation: datetime
    date_modification: datetime

    class Config:
        from_attributes = True
