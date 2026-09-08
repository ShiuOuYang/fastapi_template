from __future__ import annotations

from httpx import AsyncClient


async def test_root_health(client: AsyncClient) -> None:
    """根路徑應回傳統一格式且 success 為 True。"""
    response = await client.get("/")
    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True
    assert body["data"]["status"] == "ok"


async def test_openapi_available(client: AsyncClient) -> None:
    """OpenAPI schema 應可正常產生。"""
    response = await client.get("/openapi.json")
    assert response.status_code == 200
    assert "/api/v1/items" in response.json()["paths"]


async def test_not_found_uses_unified_format(client: AsyncClient) -> None:
    """404 也要走全域例外處理，回傳統一格式。"""
    response = await client.get("/no-such-route")
    assert response.status_code == 404
    assert response.json()["success"] is False
