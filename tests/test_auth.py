import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_register_success(client: AsyncClient):
    response = await client.post(
        "/auth/register",
        json={"email": "new@example.com", "username": "newuser", "password": "securepass"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "new@example.com"
    assert data["username"] == "newuser"
    assert "hashed_password" not in data


async def test_register_duplicate_email(client: AsyncClient):
    payload = {"email": "dup@example.com", "username": "dupuser1", "password": "password123"}
    await client.post("/auth/register", json=payload)
    payload["username"] = "dupuser2"
    response = await client.post("/auth/register", json=payload)
    assert response.status_code == 400


async def test_register_duplicate_username(client: AsyncClient):
    await client.post(
        "/auth/register",
        json={"email": "user1@example.com", "username": "sharedname", "password": "password123"},
    )
    response = await client.post(
        "/auth/register",
        json={"email": "user2@example.com", "username": "sharedname", "password": "password123"},
    )
    assert response.status_code == 400


async def test_register_short_password(client: AsyncClient):
    response = await client.post(
        "/auth/register",
        json={"email": "short@example.com", "username": "shortpw", "password": "abc"},
    )
    assert response.status_code == 422


async def test_login_success(client: AsyncClient):
    await client.post(
        "/auth/register",
        json={"email": "login@example.com", "username": "loginuser", "password": "password123"},
    )
    response = await client.post(
        "/auth/login",
        json={"email": "login@example.com", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


async def test_login_wrong_password(client: AsyncClient):
    response = await client.post(
        "/auth/login",
        json={"email": "login@example.com", "password": "wrongpass"},
    )
    assert response.status_code == 401


async def test_login_unknown_email(client: AsyncClient):
    response = await client.post(
        "/auth/login",
        json={"email": "nobody@example.com", "password": "password123"},
    )
    assert response.status_code == 401
