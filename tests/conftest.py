from __future__ import annotations

import sys
from pathlib import Path
from typing import AsyncGenerator

import pytest
import pytest_asyncio

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from httpx import ASGITransport, AsyncClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """不需要真實資料庫的 ASGI 測試 client。

    需要打到 DB 的測試，請另外覆寫 `app.dependency_overrides[get_session]`。
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
