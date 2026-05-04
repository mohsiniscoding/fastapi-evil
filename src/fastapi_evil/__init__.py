"""
fastapi-evil: A drop-in FastAPI wrapper that adds intentional request slowdowns.

    from fastapi_evil import EvilAPI

    app = EvilAPI(slow_for_millis=5_000, slow_for_methods=["GET"])
"""

from fastapi_evil.app import EvilAPI
from fastapi_evil.middleware import SlowMiddleware

# Named constant — import this instead of None to make intent explicit
ALL_METHODS: None = None

__version__ = "0.1.0"
__all__ = ["EvilAPI", "SlowMiddleware", "ALL_METHODS", "__version__"]
