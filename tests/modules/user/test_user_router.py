import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    response = await client.post(
        "/api/v1/users/register",
        json={
            "email": "test@example.com",
            "password": "securepassword123",
            "full_name": "Test User",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["full_name"] == "Test User"
    assert "id" in data
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    payload = {
        "email": "duplicate@example.com",
        "password": "securepassword123",
        "full_name": "Test User",
    }
    await client.post("/api/v1/users/register", json=payload)
    response = await client.post("/api/v1/users/register", json=payload)
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_login(client: AsyncClient):
    await client.post(
        "/api/v1/users/register",
        json={
            "email": "login@example.com",
            "password": "securepassword123",
            "full_name": "Login User",
        },
    )
    response = await client.post(
        "/api/v1/users/login",
        json={
            "email": "login@example.com",
            "password": "securepassword123",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    await client.post(
        "/api/v1/users/register",
        json={
            "email": "wrongpw@example.com",
            "password": "securepassword123",
            "full_name": "Test User",
        },
    )
    response = await client.post(
        "/api/v1/users/login",
        json={
            "email": "wrongpw@example.com",
            "password": "wrongpassword",
        },
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient):
    await client.post(
        "/api/v1/users/register",
        json={
            "email": "me@example.com",
            "password": "securepassword123",
            "full_name": "Me User",
        },
    )
    login_resp = await client.post(
        "/api/v1/users/login",
        json={"email": "me@example.com", "password": "securepassword123"},
    )
    token = login_resp.json()["access_token"]

    response = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["email"] == "me@example.com"


@pytest.mark.asyncio
async def test_get_current_user_unauthorized(client: AsyncClient):
    response = await client.get("/api/v1/users/me")
    assert response.status_code == 401
