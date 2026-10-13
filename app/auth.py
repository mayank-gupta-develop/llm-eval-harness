import os
import secrets

from fastapi import Header, HTTPException


def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    expected = os.environ.get("API_KEY")
    if not expected or not x_api_key or not secrets.compare_digest(
        x_api_key.encode(), expected.encode()
    ):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
