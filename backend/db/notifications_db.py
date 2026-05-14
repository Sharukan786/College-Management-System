"""Compatibility helpers for notification data in development mode."""

from backend.dev_store import DEV_STORE


def get_all_notifications() -> list[dict]:
    return list(DEV_STORE["notifications"])
