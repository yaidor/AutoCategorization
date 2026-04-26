from fastapi import APIRouter

from app.api.v1.uploads import router as uploads_router

router = APIRouter(prefix="/api/v1")
router.include_router(uploads_router)
