"""Schemas package initialization."""
from app.schemas.customer import (
    CustomerBase,
    CustomerCreate,
    CustomerUpdate,
    CustomerResponse,
    CustomerWithAddresses,
    CustomerListResponse,
)
from app.schemas.address import (
    AddressBase,
    AddressCreate,
    AddressUpdate,
    AddressResponse,
)
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    TokenResponse,
    PasswordChangeRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
    EmailConfirmation,
)
from app.schemas.event import (
    EventType,
    EventMetadata,
    CustomerEvent,
    AddressEvent,
)

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
