"""
Unit tests for SlowMiddleware — asyncio.sleep is mocked, tests run instantly.
"""
from datetime import datetime, timezone
from httpx import AsyncClient, ASGITransport

from fastapi_evil import EvilAPI


def make_app(slow_for_millis=1000, slow_for_methods=None, slow_until=None):
    app = EvilAPI(
        slow_for_millis=slow_for_millis,
        slow_for_methods=slow_for_methods,
        slow_until=slow_until,
    )

    @app.get("/x")
    async def get_x():
        return {"method": "GET"}

    @app.post("/x")
    async def post_x():
        return {"method": "POST"}

    @app.put("/x")
    async def put_x():
        return {"method": "PUT"}

    @app.delete("/x")
    async def delete_x():
        return {"method": "DELETE"}

    return app


async def test_sleep_called_with_correct_seconds(mock_sleep):
    app = make_app(slow_for_millis=3000)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        await c.get("/x")
    mock_sleep.assert_awaited_once_with(3.0)


async def test_sleep_not_called_for_excluded_method(mock_sleep):
    app = make_app(slow_for_millis=1000, slow_for_methods=["POST"])
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        await c.get("/x")
    mock_sleep.assert_not_awaited()


async def test_sleep_called_for_included_method(mock_sleep):
    app = make_app(slow_for_millis=1000, slow_for_methods=["GET"])
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        await c.get("/x")
    mock_sleep.assert_awaited_once()


async def test_methods_are_case_insensitive(mock_sleep):
    app = make_app(slow_for_millis=1000, slow_for_methods=["get", "POST"])
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        await c.get("/x")
    mock_sleep.assert_awaited_once()


async def test_sleep_not_called_after_expiry(mock_sleep):
    past = datetime(2020, 1, 1, tzinfo=timezone.utc)
    app = make_app(slow_until=past)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        await c.get("/x")
    mock_sleep.assert_not_awaited()


async def test_sleep_called_before_expiry(mock_sleep):
    future = datetime(2099, 1, 1, tzinfo=timezone.utc)
    app = make_app(slow_until=future)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        await c.get("/x")
    mock_sleep.assert_awaited_once()


async def test_all_methods_slowed_by_default(mock_sleep):
    app = make_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        await c.get("/x")
        await c.post("/x")
        await c.put("/x")
        await c.delete("/x")
    assert mock_sleep.await_count == 4


async def test_only_listed_methods_slowed(mock_sleep):
    app = make_app(slow_for_methods=["GET", "POST"])
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        await c.get("/x")      # slowed
        await c.post("/x")     # slowed
        await c.put("/x")      # not slowed
        await c.delete("/x")   # not slowed
    assert mock_sleep.await_count == 2


async def test_zero_millis_calls_sleep_with_zero(mock_sleep):
    app = make_app(slow_for_millis=0)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        await c.get("/x")
    mock_sleep.assert_awaited_once_with(0.0)
