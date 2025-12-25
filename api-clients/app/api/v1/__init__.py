"""API v1 package initialization."""
from fastapi import APIRouter
from app.api.v1 import customers, addresses, auth, admin

api_router = APIRouter()
api_router.include_router(customers.router)
api_router.include_router(addresses.router)
api_router.include_router(auth.router)
api_router.include_router(admin.router)

__all__ = ["api_router"]
