import asyncio
from typing import Any

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session_factory
from app.models import Categorization, Meeting
from app.models.job import Job, JobStatus
from app.services.categorization.mapping import build_categorization
from app.services.llm.base import LLMResponse
from app.services.llm.factory import get_llm_provider
from app.services.llm.prompt import PROMPT_VERSION

log = structlog.get_logger()


def _pending_meetings_filter(model: str, force: bool):
    if force:
        return select(Meeting)
    return (
        select(Meeting)
        .outerjoin(
            Categorization,
            (Categorization.meeting_id == Meeting.id)
            & (Categorization.prompt_version == PROMPT_VERSION)
            & (Categorization.model == model),
        )
        .where(Categorization.id.is_(None))
    )


async def create_batch_job(session: AsyncSession, force: bool) -> Job:
    provider = get_llm_provider()
    pending = (
        (await session.execute(_pending_meetings_filter(provider.model, force))).scalars().all()
    )

    job = Job(
        status=JobStatus.QUEUED,
        total=len(pending),
        completed=0,
        failed=0,
        cached=0,
        errors=[],
    )
    session.add(job)
    await session.commit()
    await session.refresh(job)
    log.info(
        "batch_job_created",
        job_id=job.id,
        total=job.total,
        provider=provider.name,
        model=provider.model,
        force=force,
    )
    return job


async def run_batch_job(job_id: int, force: bool) -> None:
    async with async_session_factory() as session:
        await _run(session, job_id, force)


async def _run(session: AsyncSession, job_id: int, force: bool) -> None:
    job = await session.get(Job, job_id)
    if job is None:
        log.error("batch_job_not_found", job_id=job_id)
        return

    provider = get_llm_provider()
    meetings = list(
        (await session.execute(_pending_meetings_filter(provider.model, force))).scalars().all()
    )

    job.status = JobStatus.RUNNING
    await session.commit()

    log.info("batch_job_started", job_id=job_id, total=len(meetings))

    async def _categorize_one(meeting: Meeting) -> tuple[int, LLMResponse | Exception]:
        try:
            response = await provider.categorize(meeting.transcript)
            return meeting.id, response
        except Exception as exc:
            return meeting.id, exc

    results = await asyncio.gather(*(_categorize_one(m) for m in meetings))

    completed = 0
    failed = 0
    errors: list[dict[str, Any]] = []

    for meeting_id, result in results:
        if isinstance(result, Exception):
            failed += 1
            errors.append({"meeting_id": meeting_id, "error": str(result)[:300]})
            log.warning("batch_meeting_failed", meeting_id=meeting_id, error=str(result)[:200])
            continue
        cat = build_categorization(meeting_id, provider, result)
        session.add(cat)
        completed += 1

    job.completed = completed
    job.failed = failed
    job.errors = errors
    if completed == 0 and failed > 0:
        job.status = JobStatus.FAILED
    else:
        job.status = JobStatus.COMPLETED

    await session.commit()
    log.info("batch_job_finished", job_id=job_id, completed=completed, failed=failed)
