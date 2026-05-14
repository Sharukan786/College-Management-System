"""Compatibility seed script for Python backend.

This replaces the legacy Node seed entrypoint.
"""

from backend.quick_seed import seed


if __name__ == "__main__":
    seed()
