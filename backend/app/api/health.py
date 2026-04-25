from fastapi import APIRouter

from app.core.config import VERSION, settings

router = APIRouter(tags=["platform"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/version")
async def get_version() -> dict[str, str]:
    return {
        "version": VERSION,
        "environment": settings.environment,
    }
