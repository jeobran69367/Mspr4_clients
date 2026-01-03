"""Custom exceptions."""
from fastapi import HTTPException, status


class CustomerNotFoundException(HTTPException):
    """Customer not found exception."""

    def __init__(self, customer_id: str):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=f"Customer {customer_id} not found")


class AddressNotFoundException(HTTPException):
    """Address not found exception."""

    def __init__(self, address_id: str):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=f"Address {address_id} not found")


class DuplicateEmailException(HTTPException):
    """Duplicate email exception."""

    def __init__(self):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")


class DuplicateSIRETException(HTTPException):
    """Duplicate SIRET exception."""

    def __init__(self):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail="SIRET already registered")


class InvalidCredentialsException(HTTPException):
    """Invalid credentials exception."""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )


class InsufficientPermissionsException(HTTPException):
    """Insufficient permissions exception."""

    def __init__(self):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
