"""Customer schemas for API validation."""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from app.models.customer import CustomerType, CustomerStatus


class CustomerBase(BaseModel):
    """Base customer schema."""
    civilite: Optional[str] = None
    nom: str = Field(..., min_length=1, max_length=100)
    prenom: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    telephone: Optional[str] = None
    mobile: Optional[str] = None
    type_client: CustomerType = CustomerType.PARTICULIER
    raison_sociale: Optional[str] = None
    siret: Optional[str] = None
    tva_intracommunautaire: Optional[str] = None
    nom_contact: Optional[str] = None
    preferences: Optional[str] = None


class CustomerCreate(CustomerBase):
    """Schema for creating a customer."""
    password: str = Field(..., min_length=8)


class CustomerUpdate(BaseModel):
    """Schema for updating a customer."""
    civilite: Optional[str] = None
    nom: Optional[str] = Field(None, min_length=1, max_length=100)
    prenom: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    telephone: Optional[str] = None
    mobile: Optional[str] = None
    raison_sociale: Optional[str] = None
    siret: Optional[str] = None
    tva_intracommunautaire: Optional[str] = None
    nom_contact: Optional[str] = None
    preferences: Optional[str] = None


class CustomerResponse(CustomerBase):
    """Schema for customer response."""
    id: UUID
    reference: str
    statut: CustomerStatus
    email_confirme: bool
    date_derniere_connexion: Optional[datetime] = None
    date_creation: datetime
    date_modification: datetime
    date_desactivation: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class CustomerWithAddresses(CustomerResponse):
    """Customer schema with addresses."""
    from app.schemas.address import AddressResponse
    adresses: List["AddressResponse"] = []
    
    class Config:
        from_attributes = True


class CustomerListResponse(BaseModel):
    """Schema for customer list response."""
    items: List[CustomerResponse]
    total: int
    page: int
    page_size: int
    pages: int
