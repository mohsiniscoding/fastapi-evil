<div align="center">

<img src="logo.png" alt="fastapi-evil" width="160">

# fastapi-evil

### 😈 *Your FastAPI. Now with more suffering.* 😈

[![PyPI version](https://img.shields.io/pypi/v/fastapi-evil.svg?color=red&label=pypi)](https://pypi.org/project/fastapi-evil/)
[![Python](https://img.shields.io/pypi/pyversions/fastapi-evil.svg)](https://pypi.org/project/fastapi-evil/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen)](#)

</div>

---

A **drop-in replacement** for `FastAPI` that adds intentional request slowdowns. One import change. Zero other code changes. Maximum mayhem.

```python
# before 😇
from fastapi import FastAPI
app = FastAPI()

# after 😈
from fastapi_evil import EvilAPI
app = EvilAPI()  # requests now take 10 seconds. you're welcome.
```

---

## Install

```bash
pip install fastapi-evil
# or with uv
uv add fastapi-evil
```

To use the `fastapi dev` CLI (Uvicorn + hot reload), install with the `standard` extra:

```bash
pip install "fastapi-evil[standard]"
# or with uv
uv add "fastapi-evil[standard]"
```

Then run your app:

```bash
# pip
fastapi dev main.py

# uv
uv run fastapi dev main.py
```

---

## Why Would Anyone Do This?

- **Chaos engineering** — stress-test your clients without a service mesh
- **Reproduce timeout bugs** — "it only happens in prod" → now it happens everywhere
- **Test retry logic** — make your HTTP clients earn it
- **Time-limited degradation** — slow things down for exactly one hour, then stop
- **Convince your boss the servers are overloaded** — _we do not endorse this_

---

## Quickstart

```python
from fastapi_evil import EvilAPI

app = EvilAPI()

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}

# Every request now waits 10 seconds before responding.
# uvicorn main:app --reload
```

---

## Parameters

`EvilAPI` accepts all standard `FastAPI` constructor arguments plus:

| Parameter | Type | Default | Description |
|---|---|---|---|
| `slow_for_millis` | `int` | `10_000` | Milliseconds to delay each request (10 seconds) |
| `slow_for_methods` | `list[str] \| None` | `None` | HTTP methods to slow. `None` = **ALL**. |
| `slow_until` | `datetime \| None` | `None` | Stop slowing after this datetime. `None` = slow forever. |

---

## Examples

### Slow only GET requests by 3 seconds

```python
from fastapi_evil import EvilAPI

app = EvilAPI(
    slow_for_millis=3_000,
    slow_for_methods=["GET"],
)
```

### Time-limited chaos — slow everything for the next hour, then stop

```python
from datetime import datetime, timedelta, timezone
from fastapi_evil import EvilAPI

app = EvilAPI(
    slow_for_millis=5_000,
    slow_until=datetime.now(timezone.utc) + timedelta(hours=1),
)
```

### Precise method targeting — slow writes only

```python
from fastapi_evil import EvilAPI

app = EvilAPI(
    slow_for_millis=2_000,
    slow_for_methods=["POST", "PUT", "PATCH", "DELETE"],
)
```

### Use the named constant for readability

```python
from fastapi_evil import EvilAPI, ALL_METHODS

app = EvilAPI(slow_for_millis=8_000, slow_for_methods=ALL_METHODS)
```

### Pass any standard FastAPI kwargs — they all work

```python
from fastapi_evil import EvilAPI

app = EvilAPI(
    title="My Suffering API",
    version="6.6.6",
    description="This API is evil and slow.",
    slow_for_millis=1_000,
)
```

---

## How It Works

`EvilAPI` subclasses `FastAPI` and wires a pure ASGI middleware (`SlowMiddleware`) that calls `asyncio.sleep` before dispatching each matched request. It uses a pure ASGI implementation (not Starlette's `BaseHTTPMiddleware`) to avoid known `ContextVar` propagation bugs. WebSocket and lifespan scopes are passed through untouched.

```
Request → SlowMiddleware → check method + slow_until → asyncio.sleep → your routes
```

---

## `slow_until` and Timezones

`slow_until` accepts any Python `datetime`. Timezone-aware datetimes are recommended:

```python
from datetime import datetime, timezone, timedelta

# Good — explicit UTC
slow_until=datetime.now(timezone.utc) + timedelta(hours=2)

# Also works — but emits a UserWarning (assumed UTC)
slow_until=datetime(2026, 12, 31, 23, 59, 59)
```

---

## Dev Setup

```bash
git clone https://github.com/mohsin/fastapi-evil
cd fastapi-evil
uv sync
uv run pytest
```

---

## Publishing

```bash
uv build
uv publish --token pypi-<your-token>
```

Get your token at [pypi.org/manage/account/token](https://pypi.org/manage/account/token/).

---

## License

[MIT](LICENSE) — do whatever evil you want with it.
