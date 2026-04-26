from typing import Annotated

import structlog
from fastapi import Header, HTTPException, status

from app.core.config import settings

API_KEY_HEADER = "X-API-Key"

log = structlog.get_logger()


async def verify_api_key(
    x_api_key: Annotated[str | None, Header(alias=API_KEY_HEADER)] = None,
) -> None:
    expected = settings.api_key
    if not expected:
        return
    if not x_api_key or x_api_key != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key inválida o ausente",
            headers={"WWW-Authenticate": "X-API-Key"},
        )
