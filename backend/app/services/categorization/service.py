import structlog
from fastapi import HTTPException
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Categorization, Meeting
from app.schemas.categorization import CategorizationResponse
from app.services.categorization.mapping import build_categorization
from app.services.llm.base import LLMError
from app.services.llm.factory import get_llm_provider
from app.services.llm.prompt import PROMPT_VERSION

log = structlog.get_logger()


async def categorize_meeting(
    meeting_id: int, session: AsyncSession, force: bool = False
) -> CategorizationResponse:
    meeting = await session.get(Meeting, meeting_id)
    if meeting is None:
        raise HTTPException(status_code=404, detail=f"Meeting {meeting_id} no encontrado")

    provider = get_llm_provider()

    if not force:
        cached_stmt = select(Categorization).where(
            Categorization.meeting_id == meeting_id,
            Categorization.prompt_version == PROMPT_VERSION,
            Categorization.model == provider.model,
        )
        cached = (await session.execute(cached_stmt)).scalar_one_or_none()
        if cached is not None:
            log.info("categorization_cache_hit", meeting_id=meeting_id, model=provider.model)
            return CategorizationResponse.model_validate(cached).model_copy(update={"cached": True})
    else:
        await session.execute(
            delete(Categorization).where(
                Categorization.meeting_id == meeting_id,
                Categorization.prompt_version == PROMPT_VERSION,
                Categorization.model == provider.model,
            )
        )

    log.info(
        "categorization_calling_llm",
        meeting_id=meeting_id,
        provider=provider.name,
        model=provider.model,
    )
    try:
        llm_response = await provider.categorize(meeting.transcript)
    except LLMError as exc:
        log.exception("categorization_llm_failed", meeting_id=meeting_id)
        raise HTTPException(status_code=502, detail=f"LLM error: {exc}") from exc

    cat = build_categorization(meeting_id, provider, llm_response)
    session.add(cat)
    await session.commit()
    await session.refresh(cat)
    return CategorizationResponse.model_validate(cat).model_copy(update={"cached": False})
