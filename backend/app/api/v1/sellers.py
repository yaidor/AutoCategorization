from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models import Seller

router = APIRouter(prefix="/sellers", tags=["sellers"])


class SellerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


@router.get("")
async def list_sellers(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> list[SellerOut]:
    rows = (await session.execute(select(Seller).order_by(Seller.name))).scalars().all()
    return [SellerOut.model_validate(s) for s in rows]
