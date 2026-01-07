"""Repositories package initialization."""

from app.repositories.address_repository import AddressRepository
from app.repositories.base_repository import BaseRepository
from app.repositories.customer_repository import CustomerRepository

__all__ = [
    "BaseRepository",
    "CustomerRepository",
    "AddressRepository",
]
