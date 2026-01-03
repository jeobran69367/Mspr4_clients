"""Tests for address endpoints."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from tests.factories import create_test_customer, create_test_address


@pytest.mark.asyncio
async def test_create_address(client: AsyncClient, db_session: AsyncSession):
    """Test creating a new address."""
    # Create test customer
    customer = create_test_customer()
    db_session.add(customer)
    await db_session.commit()

    # Login
    login_response = await client.post("/api/v1/auth/login", json={"email": customer.email, "password": "password123"})
    token = login_response.json()["access_token"]

    # Create address
    address_data = {
        "type_adresse": "livraison",
        "est_defaut": True,
        "libelle": "Domicile",
        "destinataire": "Test User",
        "adresse_ligne1": "123 Test Street",
        "code_postal": "75001",
        "ville": "Paris",
        "pays": "France",
    }

    response = await client.post("/api/v1/addresses/", json=address_data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 201
    data = response.json()
    assert data["ville"] == address_data["ville"]
    assert data["est_defaut"] is True


@pytest.mark.asyncio
async def test_list_addresses(client: AsyncClient, db_session: AsyncSession):
    """Test listing customer addresses."""
    # Create test customer with address
    customer = create_test_customer()
    db_session.add(customer)
    await db_session.commit()

    address = create_test_address(customer.id)
    db_session.add(address)
    await db_session.commit()

    # Login
    login_response = await client.post("/api/v1/auth/login", json={"email": customer.email, "password": "password123"})
    token = login_response.json()["access_token"]

    # List addresses
    response = await client.get("/api/v1/addresses/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["ville"] == address.ville
