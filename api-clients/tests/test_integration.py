"""Integration tests."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_customer_lifecycle(client: AsyncClient, db_session: AsyncSession):
    """Test complete customer lifecycle."""
    # 1. Create customer
    customer_data = {
        "civilite": "Mme",
        "nom": "Lifecycle",
        "prenom": "Test",
        "email": "lifecycle@example.com",
        "telephone": "0123456789",
        "type_client": "particulier",
        "password": "password123",
    }

    create_response = await client.post("/api/v1/customers/", json=customer_data)
    assert create_response.status_code == 201

    # 2. Login
    login_response = await client.post("/api/v1/auth/login", json={"email": customer_data["email"], "password": "password123"})
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # 3. Get customer info
    get_response = await client.get("/api/v1/customers/me", headers={"Authorization": f"Bearer {token}"})
    if get_response.status_code != 200:
        print(f"Error getting customer: {get_response.status_code} - {get_response.text}")
    assert get_response.status_code == 200

    # 4. Add address
    address_data = {
        "type_adresse": "livraison",
        "est_defaut": True,
        "adresse_ligne1": "123 Test Street",
        "code_postal": "75001",
        "ville": "Paris",
        "pays": "France",
    }

    address_response = await client.post("/api/v1/addresses/", json=address_data, headers={"Authorization": f"Bearer {token}"})
    assert address_response.status_code == 201

    # 5. List addresses
    list_response = await client.get("/api/v1/addresses/", headers={"Authorization": f"Bearer {token}"})
    assert list_response.status_code == 200
    addresses = list_response.json()
    assert len(addresses) == 1
