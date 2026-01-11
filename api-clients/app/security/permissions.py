"""Permissions and roles management."""

from enum import Enum
from typing import List

from app.models.customer import CustomerType


class Permission(str, Enum):
    """Permission enumeration."""

    READ_CUSTOMER = "read:customer"
    WRITE_CUSTOMER = "write:customer"
    DELETE_CUSTOMER = "delete:customer"
    READ_ALL_CUSTOMERS = "read:all_customers"
    WRITE_ALL_CUSTOMERS = "write:all_customers"
    DELETE_ALL_CUSTOMERS = "delete:all_customers"
    ADMIN = "admin"


ROLE_PERMISSIONS = {
    CustomerType.PARTICULIER: [
        Permission.READ_CUSTOMER,
        Permission.WRITE_CUSTOMER,
    ],
    CustomerType.PROFESSIONNEL: [
        Permission.READ_CUSTOMER,
        Permission.WRITE_CUSTOMER,
    ],
    CustomerType.DISTRIBUTEUR: [
        Permission.READ_CUSTOMER,
        Permission.WRITE_CUSTOMER,
    ],
    CustomerType.ADMIN: [
        Permission.READ_CUSTOMER,
        Permission.WRITE_CUSTOMER,
        Permission.DELETE_CUSTOMER,
        Permission.READ_ALL_CUSTOMERS,
        Permission.WRITE_ALL_CUSTOMERS,
        Permission.DELETE_ALL_CUSTOMERS,
        Permission.ADMIN,
    ],
}


def has_permission(customer_type: CustomerType, permission: Permission) -> bool:
    """Check if a customer type has a specific permission."""
    permissions = ROLE_PERMISSIONS.get(customer_type, [])
    return permission in permissions


def get_permissions(customer_type: CustomerType) -> List[Permission]:
    """Get all permissions for a customer type."""
    return ROLE_PERMISSIONS.get(customer_type, [])
