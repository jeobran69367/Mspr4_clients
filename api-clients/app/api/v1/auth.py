"""Authentication API endpoints."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.dependencies import get_current_active_user
from app.models.customer import Customer
from app.schemas.auth import (
    EmailConfirmation,
    LoginRequest,
    LoginResponse,
    PasswordChangeRequest,
    RefreshTokenRequest,
    TokenResponse,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", response_model=LoginResponse)
async def login(login_data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Authenticate user and return tokens."""
    service = AuthService(db)
    customer, access_token, refresh_token = await service.authenticate(login_data.email, login_data.password)

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(token_data: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    """Refresh access token using refresh token."""
    service = AuthService(db)
    access_token = await service.refresh_access_token(token_data.refresh_token)

    return TokenResponse(access_token=access_token, token_type="bearer")


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    password_data: PasswordChangeRequest,
    current_user: Customer = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Change current user's password."""
    service = AuthService(db)
    await service.change_password(str(current_user.id), password_data.old_password, password_data.new_password)


@router.post("/confirm-email", status_code=status.HTTP_200_OK)
async def confirm_email(confirmation: EmailConfirmation, db: AsyncSession = Depends(get_db)):
    """Confirm user email address."""
    service = AuthService(db)
    customer = await service.confirm_email(confirmation.token)
    return {"message": "Email confirmed successfully", "email": customer.email}


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(current_user: Customer = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)):
    """Logout current user (client-side token deletion)."""
    # Revoke all refresh tokens for the current user
    service = AuthService(db)
    await service.logout(customer_id=str(current_user.id))
    return
