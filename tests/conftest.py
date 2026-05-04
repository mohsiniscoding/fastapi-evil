import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch

from fastapi_evil import EvilAPI


@pytest.fixture
def fast_app() -> EvilAPI:
    app = EvilAPI(slow_for_millis=10)

    @app.get("/ping")
    async def ping():
        return {"ok": True}

    return app


@pytest_asyncio.fixture
async def client(fast_app: EvilAPI):
    async with AsyncClient(
        transport=ASGITransport(app=fast_app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture
def mock_sleep():
    with patch("fastapi_evil.middleware.asyncio.sleep", new_callable=AsyncMock) as m:
        yield m
