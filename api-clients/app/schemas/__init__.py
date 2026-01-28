"""Schemas package initialization."""

from app.schemas.address import AddressBase, AddressCreate, AddressResponse, AddressUpdate
from app.schemas.auth import (
    EmailConfirmation,
    LoginRequest,
    LoginResponse,
    PasswordChangeRequest,
    PasswordResetConfirm,
    PasswordResetRequest,
    RefreshTokenRequest,
    TokenResponse,
)
from app.schemas.customer import (
    CustomerBase,
    CustomerCreate,
    CustomerListResponse,
    CustomerResponse,
    CustomerUpdate,
    CustomerWithAddresses,
)
from app.schemas.event import AddressEvent, CustomerEvent, EventMetadata, EventType

__all__ = [
    "CustomerBase",
    "CustomerCreate",
    "CustomerUpdate",
    "CustomerResponse",
    "CustomerWithAddresses",
    "CustomerListResponse",
    "AddressBase",
    "AddressCreate",
    "AddressUpdate",
    "AddressResponse",
    "LoginRequest",
    "LoginResponse",
    "RefreshTokenRequest",
    "TokenResponse",
    "PasswordChangeRequest",
    "PasswordResetRequest",
    "PasswordResetConfirm",
    "EmailConfirmation",
    "EventType",
    "EventMetadata",
    "CustomerEvent",
    "AddressEvent",
]
