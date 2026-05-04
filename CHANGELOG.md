# Changelog

All notable changes to `fastapi-evil` will be documented here.

## [0.1.0] — 2026-05-04

### Added
- `EvilAPI` class — drop-in subclass of `FastAPI`
- `SlowMiddleware` — pure ASGI middleware with configurable delays
- `slow_for_millis` parameter (default: 10,000ms)
- `slow_for_methods` parameter — restrict slowdowns to specific HTTP verbs
- `slow_until` parameter — time-limited chaos with automatic expiry
- UTC normalization for naive `slow_until` datetimes (emits `UserWarning`)
- `ALL_METHODS` named constant exported from package root
