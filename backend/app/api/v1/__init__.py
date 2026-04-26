from fastapi import APIRouter, Depends

from app.api.v1.customers import router as customers_router
from app.api.v1.jobs import router as jobs_router
from app.api.v1.meetings import router as meetings_router
from app.api.v1.metrics import router as metrics_router
from app.api.v1.sellers import router as sellers_router
from app.api.v1.uploads import router as uploads_router
from app.core.security import verify_api_key

router = APIRouter(prefix="/api/v1", dependencies=[Depends(verify_api_key)])
router.include_router(uploads_router)
router.include_router(meetings_router)
router.include_router(jobs_router)
router.include_router(metrics_router)
router.include_router(sellers_router)
router.include_router(customers_router)
