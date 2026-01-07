"""Tests for customer endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import create_test_customer


@pytest.mark.asyncio
async def test_create_customer(client: AsyncClient):
    """Test creating a new customer."""
    customer_data = {
        "civilite": "M",
        "nom": "Test",
        "prenom": "User",
        "email": "testuser@example.com",
        "telephone": "0123456789",
        "type_client": "particulier",
        "password": "password123",
    }

    response = await client.post("/api/v1/customers/", json=customer_data)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == customer_data["email"]
    assert data["nom"] == customer_data["nom"]
    assert "id" in data
    assert "reference" in data


@pytest.mark.asyncio
async def test_get_customer_me(client: AsyncClient, db_session: AsyncSession):
    """Test getting current customer."""
    # Create test customer
    customer = create_test_customer()
    db_session.add(customer)
    await db_session.commit()

    # Login to get token
    login_response = await client.post("/api/v1/auth/login", json={"email": customer.email, "password": "password123"})
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Get current customer
    response = await client.get("/api/v1/customers/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == customer.email


@pytest.mark.asyncio
async def test_update_customer(client: AsyncClient, db_session: AsyncSession):
    """Test updating a customer."""
    # Create test customer
    customer = create_test_customer()
    db_session.add(customer)
    await db_session.commit()

    # Login to get token
    login_response = await client.post("/api/v1/auth/login", json={"email": customer.email, "password": "password123"})
    token = login_response.json()["access_token"]

    # Update customer
    update_data = {"telephone": "0987654321"}
    response = await client.put(
        f"/api/v1/customers/{customer.id}", json=update_data, headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["telephone"] == update_data["telephone"]
