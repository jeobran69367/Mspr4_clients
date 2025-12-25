"""Utilities package initialization."""
from app.utils.exceptions import (
    CustomerNotFoundException,
    AddressNotFoundException,
    DuplicateEmailException,
    DuplicateSIRETException,
    InvalidCredentialsException,
    InsufficientPermissionsException,
)
from app.utils.validators import (
    validate_email,
    validate_phone,
    validate_siret,
    validate_postal_code,
    validate_tva_intracommunautaire,
)
from app.utils.formatters import (
    format_phone_number,
    format_siret,
    format_date,
    format_customer_name,
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
