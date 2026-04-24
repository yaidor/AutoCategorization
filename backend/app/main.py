from fastapi import FastAPI

from app.core.config import settings

app = FastAPI(
    title="SalesCat API",
    version="0.1.0",
    description="Ingesta y categorización de reuniones de ventas.",
)


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "service": "salescat-api",
        "status": "ok",
        "environment": settings.environment,
    }
