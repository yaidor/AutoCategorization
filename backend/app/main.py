from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.api.v1 import router as v1_router
from app.core.config import VERSION, settings
from app.core.logging import configure_logging
from app.core.middleware import RequestIDMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    log = structlog.get_logger()
    log.info("startup", environment=settings.environment, version=VERSION)
    yield
    log.info("shutdown")


def create_app() -> FastAPI:
    configure_logging(settings.log_level, settings.environment)

    app = FastAPI(
        title="SalesCat API",
        version=VERSION,
        description="Ingesta y categorización de reuniones de ventas.",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestIDMiddleware)

    app.include_router(health_router)
    app.include_router(v1_router)

    @app.get("/")
    async def root() -> dict[str, str]:
        return {
            "service": "salescat-api",
            "status": "ok",
            "environment": settings.environment,
        }

    return app


app = create_app()
