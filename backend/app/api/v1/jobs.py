from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.job import Job
from app.schemas.categorization import JobResponse

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/{job_id}")
async def get_job_endpoint(
    job_id: int,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> JobResponse:
    job = await session.get(Job, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} no encontrado")
    return JobResponse.model_validate(job)
