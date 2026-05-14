"""Compatibility entrypoint for FastAPI backend.

Run with:
    python -m backend.index
"""

import os

import uvicorn


def main() -> None:
    port = int(os.getenv("PORT", "5000"))
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port, reload=True)


if __name__ == "__main__":
    main()
