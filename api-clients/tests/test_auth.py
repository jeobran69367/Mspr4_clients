"""Tests for authentication endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import create_test_customer


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, db_session: AsyncSession):
    """Test successful login."""
    # Create test customer
    customer = create_test_customer()
    db_session.add(customer)
    await db_session.commit()

    # Login
    response = await client.post("/api/v1/auth/login", json={"email": customer.email, "password": "password123"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient, db_session: AsyncSession):
    """Test login with invalid credentials."""
    # Create test customer
    customer = create_test_customer()
    db_session.add(customer)
    await db_session.commit()

    # Login with wrong password
    response = await client.post("/api/v1/auth/login", json={"email": customer.email, "password": "wrongpassword"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_change_password(client: AsyncClient, db_session: AsyncSession):
    """Test changing password."""
    # Create test customer
    customer = create_test_customer()
    db_session.add(customer)
    await db_session.commit()

    # Login
    login_response = await client.post("/api/v1/auth/login", json={"email": customer.email, "password": "password123"})
    token = login_response.json()["access_token"]

    # Change password
    response = await client.post(
        "/api/v1/auth/change-password",
        json={"old_password": "password123", "new_password": "newpassword123"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 204

    # Try to login with new password
    new_login_response = await client.post("/api/v1/auth/login", json={"email": customer.email, "password": "newpassword123"})
    assert new_login_response.status_code == 200


@pytest.mark.asyncio
async def test_refresh_requires_db_token(client: AsyncClient, db_session: AsyncSession):
    """Ensure refresh only works if token exists in DB."""
    customer = create_test_customer()
    db_session.add(customer)
    await db_session.commit()

    # Login to get tokens (this will store refresh token in DB via service)
    login_response = await client.post("/api/v1/auth/login", json={"email": customer.email, "password": "password123"})
    assert login_response.status_code == 200
    refresh_token = login_response.json()["refresh_token"]

    # Refresh should work
    refresh_response = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert refresh_response.status_code == 200

    # Manually delete the refresh token from DB to simulate revocation
    await db_session.execute("DELETE FROM user_auth WHERE refresh_token = :token", {"token": refresh_token})
    await db_session.commit()

    # Now refresh should fail
    refresh_response2 = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert refresh_response2.status_code == 401


@pytest.mark.asyncio
async def test_logout_revokes_tokens(client: AsyncClient, db_session: AsyncSession):
    customer = create_test_customer()
    db_session.add(customer)
    await db_session.commit()

    # Login to get tokens
    login_response = await client.post("/api/v1/auth/login", json={"email": customer.email, "password": "password123"})
    token = login_response.json()["access_token"]
    refresh_token = login_response.json()["refresh_token"]

    # Logout (revokes all tokens for user)
    response = await client.post("/api/v1/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 204

    # Refresh should now fail
    refresh_response = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert refresh_response.status_code == 401
