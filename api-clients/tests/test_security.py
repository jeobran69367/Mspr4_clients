"""Additional unit tests to increase coverage for authentication and security."""

import uuid
from datetime import timedelta

import pytest

from app.security.auth import create_access_token, create_refresh_token, decode_token, verify_token
from app.security.passwords import hash_password, verify_password
from tests.factories import create_test_customer
from app.models.user_auth import UserAuth


@pytest.mark.unit
def test_password_hash_and_verify():
    pw = "a-very-strong-password-🤖"
    hashed = hash_password(pw)
    assert hashed != pw
    assert verify_password(pw, hashed)
    assert not verify_password("wrongpw", hashed)


@pytest.mark.unit
def test_jwt_create_and_decode():
    data = {"sub": "12345", "role": "user"}
    token = create_access_token(data, expires_delta=timedelta(minutes=1))
    payload = decode_token(token)
    assert payload.get("sub") == "12345"
    assert payload.get("type") == "access"
    assert verify_token(token, token_type="access") == "12345"


@pytest.mark.asyncio
async def test_user_auth_repository_crud(db_session):
    # create a dummy UserAuth and store it
    from datetime import datetime, timedelta

    ua = UserAuth(
        id=uuid.uuid4(),
        customer_id=uuid.uuid4(),
        refresh_token="rt-123",
        token_expiry=datetime.utcnow() + timedelta(days=1),
    )
    db_session.add(ua)
    await db_session.commit()

    # import repository here to avoid circular imports at module import time
    from app.repositories.user_auth_repository import UserAuthRepository

    repo = UserAuthRepository(db_session)
    found = await repo.get_by_token("rt-123")
    assert found is not None
    assert found.refresh_token == "rt-123"

    # delete by token
    await repo.delete_by_token("rt-123")
    found2 = await repo.get_by_token("rt-123")
    assert found2 is None


@pytest.mark.asyncio
async def test_auth_service_flow(client, db_session):
    # create a test customer using the factory
    customer = create_test_customer()
    db_session.add(customer)
    await db_session.commit()

    # login via endpoint
    resp = await client.post("/api/v1/auth/login", json={"email": customer.email, "password": "password123"})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data and "refresh_token" in data

    # refresh should work
    rf = data["refresh_token"]
    rresp = await client.post("/api/v1/auth/refresh", json={"refresh_token": rf})
    assert rresp.status_code == 200

    # logout should revoke
    access = data["access_token"]
    lresp = await client.post("/api/v1/auth/logout", headers={"Authorization": f"Bearer {access}"})
    assert lresp.status_code == 204

    # now refresh should fail
    rresp2 = await client.post("/api/v1/auth/refresh", json={"refresh_token": rf})
    assert rresp2.status_code == 401
