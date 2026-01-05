"""Utilities package initialization."""
from app.utils.exceptions import (
    AddressNotFoundException,
    CustomerNotFoundException,
    DuplicateEmailException,
    DuplicateSIRETException,
    InsufficientPermissionsException,
    InvalidCredentialsException,
)
from app.utils.formatters import format_customer_name, format_date, format_phone_number, format_siret
from app.utils.validators import (
    validate_email,
    validate_phone,
    validate_postal_code,
    validate_siret,
    validate_tva_intracommunautaire,
)

__all__ = [
    "CustomerNotFoundException",
    "AddressNotFoundException",
    "DuplicateEmailException",
    "DuplicateSIRETException",
    "InvalidCredentialsException",
    "InsufficientPermissionsException",
    "validate_email",
    "validate_phone",
    "validate_siret",
    "validate_postal_code",
    "validate_tva_intracommunautaire",
    "format_phone_number",
    "format_siret",
    "format_date",
    "format_customer_name",
]
