import asyncio
import warnings
from datetime import datetime, timezone

from starlette.types import ASGIApp, Receive, Scope, Send


class SlowMiddleware:
    """
    Pure ASGI middleware that injects an intentional delay before each matched request.

    Preferred over BaseHTTPMiddleware to avoid Starlette's known ContextVar
    propagation bug in BaseHTTPMiddleware.
    """

    def __init__(
        self,
        app: ASGIApp,
        *,
        slow_for_millis: int = 10_000,
        slow_for_methods: list[str] | None = None,
        slow_until: datetime | None = None,
    ) -> None:
        self.app = app
        self.slow_for_millis = slow_for_millis

        self.slow_for_methods: frozenset[str] | None = (
            frozenset(m.upper() for m in slow_for_methods)
            if slow_for_methods is not None
            else None
        )

        if slow_until is not None and slow_until.tzinfo is None:
            warnings.warn(
                "slow_until is a naive datetime; interpreting as UTC. "
                "Pass a timezone-aware datetime (e.g. datetime.now(timezone.utc) + timedelta(...)) "
                "to suppress this warning.",
                UserWarning,
                stacklevel=3,
            )
            slow_until = slow_until.replace(tzinfo=timezone.utc)
        self.slow_until = slow_until

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        if self._should_slow(scope):
            await asyncio.sleep(self.slow_for_millis / 1000)

        await self.app(scope, receive, send)

    def _should_slow(self, scope: Scope) -> bool:
        if self.slow_until is not None:
            if datetime.now(tz=timezone.utc) >= self.slow_until:
                return False

        if self.slow_for_methods is not None:
            if scope.get("method", "").upper() not in self.slow_for_methods:
                return False

        return True
