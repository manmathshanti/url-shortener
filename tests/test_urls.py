import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch

pytestmark = pytest.mark.asyncio

VALID_URL = "https://www.example.com/some/long/path"


async def test_create_url_success(client: AsyncClient, auth_headers: dict):
    response = await client.post(
        "/urls",
        json={"original_url": VALID_URL},
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["original_url"] == VALID_URL
    assert "short_code" in data
    assert "short_url" in data
    assert data["total_clicks"] == 0


async def test_create_url_with_custom_alias(client: AsyncClient, auth_headers: dict):
    response = await client.post(
        "/urls",
        json={"original_url": VALID_URL, "custom_alias": "myalias"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    assert response.json()["short_code"] == "myalias"


async def test_create_url_duplicate_alias(client: AsyncClient, auth_headers: dict):
    await client.post(
        "/urls",
        json={"original_url": VALID_URL, "custom_alias": "dupcode"},
        headers=auth_headers,
    )
    response = await client.post(
        "/urls",
        json={"original_url": VALID_URL, "custom_alias": "dupcode"},
        headers=auth_headers,
    )
    assert response.status_code == 409


async def test_create_url_invalid_url(client: AsyncClient, auth_headers: dict):
    response = await client.post(
        "/urls",
        json={"original_url": "not-a-url"},
        headers=auth_headers,
    )
    assert response.status_code == 422


async def test_create_url_unauthenticated(client: AsyncClient):
    response = await client.post("/urls", json={"original_url": VALID_URL})
    assert response.status_code == 403


async def test_list_urls(client: AsyncClient, auth_headers: dict):
    response = await client.get("/urls", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


async def test_delete_url(client: AsyncClient, auth_headers: dict):
    create_resp = await client.post(
        "/urls",
        json={"original_url": VALID_URL},
        headers=auth_headers,
    )
    short_code = create_resp.json()["short_code"]

    delete_resp = await client.delete(f"/urls/{short_code}", headers=auth_headers)
    assert delete_resp.status_code == 204


async def test_delete_nonexistent_url(client: AsyncClient, auth_headers: dict):
    response = await client.delete("/urls/doesnotexist", headers=auth_headers)
    assert response.status_code == 404


async def test_get_analytics(client: AsyncClient, auth_headers: dict):
    create_resp = await client.post(
        "/urls",
        json={"original_url": VALID_URL},
        headers=auth_headers,
    )
    short_code = create_resp.json()["short_code"]

    analytics_resp = await client.get(f"/urls/{short_code}/analytics", headers=auth_headers)
    assert analytics_resp.status_code == 200
    data = analytics_resp.json()
    assert data["short_code"] == short_code
    assert data["total_clicks"] == 0
