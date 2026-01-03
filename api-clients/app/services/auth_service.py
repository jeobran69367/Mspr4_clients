"""Authentication service with business logic."""
from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.models.customer import Customer
from app.models.user_auth import UserAuth
from app.repositories.customer_repository import CustomerRepository
from app.security.auth import create_access_token, create_refresh_token, verify_token
from app.security.passwords import verify_password, hash_password
from app.config import settings
import uuid


class AuthService:
    """Authentication service with business logic."""

    def __init__(self, db: AsyncSession):
        """Initialize authentication service."""
        self.db = db
        self.customer_repository = CustomerRepository(db)

    async def authenticate(
        self,
        email: str,
        password: str
    ) -> Tuple[Customer, str, str]:
        """Authenticate a user and return tokens."""
        # Get customer
        customer = await self.customer_repository.get_by_email(email)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        # Verify password
        if not customer.hashed_password or not verify_password(password, customer.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        # Check if account is active
        if customer.statut != "actif" and customer.statut != "en_attente":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is not active"
            )

        # Update last connection
        customer.date_derniere_connexion = datetime.utcnow()
        await self.customer_repository.update(customer)

        # Create tokens
        access_token = create_access_token({"sub": str(customer.id)})
        refresh_token = create_refresh_token({"sub": str(customer.id)})

        # Store refresh token
        user_auth = UserAuth(
            id=uuid.uuid4(),
            customer_id=customer.id,
            refresh_token=refresh_token,
            token_expiry=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )
        self.db.add(user_auth)
        await self.db.commit()

        return customer, access_token, refresh_token

    async def refresh_access_token(self, refresh_token: str) -> str:
        """Refresh access token using refresh token."""
        # Verify refresh token
        customer_id = verify_token(refresh_token, token_type="refresh")
        if not customer_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        # Get customer
        customer = await self.customer_repository.get_by_id(customer_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Customer not found"
            )

        # Create new access token
        access_token = create_access_token({"sub": str(customer.id)})
        return access_token

    async def change_password(
        self,
        customer_id: str,
        old_password: str,
        new_password: str
    ) -> None:
        """Change customer password."""
        customer = await self.customer_repository.get_by_id(customer_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )

        # Verify old password
        if not customer.hashed_password or not verify_password(old_password, customer.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password"
            )

        # Update password
        customer.hashed_password = hash_password(new_password)
        await self.customer_repository.update(customer)

    async def confirm_email(self, token: str) -> Customer:
        """Confirm customer email."""
        # Verify token
        customer_id = verify_token(token, token_type="access")
        if not customer_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired token"
            )

        # Get and update customer
        customer = await self.customer_repository.get_by_id(customer_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )

        customer.email_confirme = True
        if customer.statut == "en_attente":
            customer.statut = "actif"

        return await self.customer_repository.update(customer)
