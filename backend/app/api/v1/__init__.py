from fastapi import APIRouter

from app.api.v1.jobs import router as jobs_router
from app.api.v1.meetings import router as meetings_router
from app.api.v1.uploads import router as uploads_router

router = APIRouter(prefix="/api/v1")
router.include_router(uploads_router)
router.include_router(meetings_router)
router.include_router(jobs_router)
