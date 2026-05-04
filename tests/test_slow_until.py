"""
Tests for slow_until behaviour — uses freezegun for deterministic datetime control.
"""
import warnings
from datetime import datetime, timezone, timedelta

from freezegun import freeze_time
from httpx import AsyncClient, ASGITransport

from fastapi_evil import EvilAPI


def make_app(slow_until):
    app = EvilAPI(slow_for_millis=1000, slow_until=slow_until)

    @app.get("/x")
    async def x():
        return {}

    return app


async def test_slows_when_before_deadline(mock_sleep):
    deadline = datetime(2026, 1, 1, 13, 0, 0, tzinfo=timezone.utc)
    app = make_app(slow_until=deadline)
    with freeze_time("2026-01-01 12:00:00+00:00"):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            await c.get("/x")
    mock_sleep.assert_awaited_once()


async def test_does_not_slow_after_deadline(mock_sleep):
    deadline = datetime(2026, 1, 1, 13, 0, 0, tzinfo=timezone.utc)
    app = make_app(slow_until=deadline)
    with freeze_time("2026-01-01 14:00:00+00:00"):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            await c.get("/x")
    mock_sleep.assert_not_awaited()


async def test_does_not_slow_at_exact_deadline(mock_sleep):
    deadline = datetime(2026, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
    app = make_app(slow_until=deadline)
    with freeze_time("2026-06-01 12:00:00+00:00"):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            await c.get("/x")
    mock_sleep.assert_not_awaited()


async def test_none_slow_until_slows_forever(mock_sleep):
    app = EvilAPI(slow_for_millis=1000, slow_until=None)

    @app.get("/x")
    async def x():
        return {}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        await c.get("/x")
    mock_sleep.assert_awaited_once()


async def test_naive_datetime_emits_userwarning():
    # Starlette builds the middleware stack lazily on first request,
    # so the warning fires when the first request triggers stack construction.
    naive = datetime(2030, 6, 1, 12, 0, 0)
    app = EvilAPI(slow_for_millis=1, slow_until=naive)

    @app.get("/x")
    async def x():
        return {}

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            await c.get("/x")

    naive_warnings = [
        w for w in caught
        if issubclass(w.category, UserWarning) and "naive" in str(w.message).lower()
    ]
    assert len(naive_warnings) == 1


async def test_naive_datetime_treated_as_utc(mock_sleep):
    far_future = datetime(2099, 1, 1, 0, 0, 0)  # naive
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        app = EvilAPI(slow_for_millis=1000, slow_until=far_future)

    @app.get("/x")
    async def x():
        return {}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        await c.get("/x")
    mock_sleep.assert_awaited_once()


async def test_timezone_aware_datetime_works(mock_sleep):
    deadline = datetime.now(timezone.utc) + timedelta(hours=24)
    app = make_app(slow_until=deadline)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        await c.get("/x")
    mock_sleep.assert_awaited_once()
