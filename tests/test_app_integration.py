"""
Integration tests — real ASGI round-trips with a tiny 10ms delay.
Verifies that EvilAPI behaves exactly like FastAPI for all HTTP concerns.
"""
import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI
from pydantic import BaseModel

from fastapi_evil import EvilAPI


async def test_ping_returns_200(client: AsyncClient):
    response = await client.get("/ping")
    assert response.status_code == 200
    assert response.json() == {"ok": True}


async def test_evilapi_is_instance_of_fastapi():
    app = EvilAPI(slow_for_millis=1)
    assert isinstance(app, FastAPI)


async def test_fastapi_kwargs_pass_through():
    app = EvilAPI(slow_for_millis=1, title="My Evil API", version="9.9.9", description="for chaos")
    assert app.title == "My Evil API"
    assert app.version == "9.9.9"
    assert app.description == "for chaos"


async def test_path_params_work():
    app = EvilAPI(slow_for_millis=1)

    @app.get("/items/{item_id}")
    async def get_item(item_id: int):
        return {"item_id": item_id}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        response = await c.get("/items/42")
    assert response.status_code == 200
    assert response.json() == {"item_id": 42}


async def test_request_body_works():
    class Item(BaseModel):
        name: str
        value: int

    app = EvilAPI(slow_for_millis=1)

    @app.post("/items")
    async def create_item(item: Item):
        return item

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        response = await c.post("/items", json={"name": "sword", "value": 666})
    assert response.status_code == 200
    assert response.json() == {"name": "sword", "value": 666}


async def test_query_params_work():
    app = EvilAPI(slow_for_millis=1)

    @app.get("/search")
    async def search(q: str, limit: int = 10):
        return {"q": q, "limit": limit}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        response = await c.get("/search", params={"q": "chaos", "limit": 5})
    assert response.status_code == 200
    assert response.json() == {"q": "chaos", "limit": 5}


async def test_404_still_works():
    app = EvilAPI(slow_for_millis=1)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        response = await c.get("/does-not-exist")
    assert response.status_code == 404


async def test_openapi_schema_generated():
    app = EvilAPI(slow_for_millis=1, title="Evil Docs")

    @app.get("/hello")
    async def hello():
        return {"hello": "world"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        response = await c.get("/openapi.json")
    assert response.status_code == 200
    assert response.json()["info"]["title"] == "Evil Docs"
