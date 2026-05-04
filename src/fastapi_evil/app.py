from datetime import datetime
from typing import Any

from fastapi import FastAPI

from fastapi_evil.middleware import SlowMiddleware


class EvilAPI(FastAPI):
    """
    A drop-in replacement for FastAPI that adds intentional request slowdowns.

    All standard FastAPI constructor parameters are supported.

    Parameters
    ----------
    slow_for_millis : int
        Milliseconds to delay every matched request. Default: 10_000 (10 seconds).
    slow_for_methods : list[str] | None
        HTTP methods to slow (case-insensitive). None = ALL methods.
        Example: ["GET", "POST"] slows only reads and creates.
    slow_until : datetime | None
        Stop slowing after this point in time. None = slow forever.
        Naive datetimes are assumed UTC and trigger a UserWarning.

    Examples
    --------
    >>> app = EvilAPI()  # slow everything, forever

    >>> from datetime import datetime, timedelta, timezone
    >>> app = EvilAPI(
    ...     slow_for_millis=3_000,
    ...     slow_for_methods=["GET"],
    ...     slow_until=datetime.now(timezone.utc) + timedelta(hours=1),
    ... )
    """

    def __init__(
        self,
        *,
        slow_for_millis: int = 10_000,
        slow_for_methods: list[str] | None = None,
        slow_until: datetime | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.add_middleware(
            SlowMiddleware,
            slow_for_millis=slow_for_millis,
            slow_for_methods=slow_for_methods,
            slow_until=slow_until,
        )
