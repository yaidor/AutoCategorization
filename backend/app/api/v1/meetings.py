from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.categorization import CategorizationResponse, JobResponse
from app.services.categorization.batch import create_batch_job, run_batch_job
from app.services.categorization.service import categorize_meeting

router = APIRouter(prefix="/meetings", tags=["meetings"])


@router.post("/{meeting_id}/categorize")
async def categorize_meeting_endpoint(
    meeting_id: int,
    session: Annotated[AsyncSession, Depends(get_session)],
    force: bool = False,
) -> CategorizationResponse:
    return await categorize_meeting(meeting_id, session, force=force)


@router.post("/batch-categorize", status_code=202)
async def batch_categorize_endpoint(
    background_tasks: BackgroundTasks,
    session: Annotated[AsyncSession, Depends(get_session)],
    force: bool = False,
) -> JobResponse:
    job = await create_batch_job(session, force=force)
    background_tasks.add_task(run_batch_job, job.id, force)
    return JobResponse.model_validate(job)
