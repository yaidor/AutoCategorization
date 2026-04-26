from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.ingest import IngestSummary
from app.services.csv_ingest import ingest_csv

router = APIRouter(prefix="/uploads", tags=["uploads"])


@router.post("/csv", status_code=200)
async def upload_csv(
    file: Annotated[UploadFile, File(...)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> IngestSummary:
    data = await file.read()
    return await ingest_csv(data, session)
