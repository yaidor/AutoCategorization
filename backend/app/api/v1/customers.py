from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.enums import Industry
from app.schemas.customers import CustomerDetailResponse, CustomerListPage
from app.services.customers import SortField, get_customer_detail, list_customers

router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("")
async def list_customers_endpoint(
    session: Annotated[AsyncSession, Depends(get_session)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    sort: SortField = "meeting_date_desc",
    search: str | None = None,
    seller_id: int | None = None,
    industry: Industry | None = None,
    closed: bool | None = None,
    from_date: Annotated[date | None, Query(alias="from")] = None,
    to_date: Annotated[date | None, Query(alias="to")] = None,
    uncategorized: bool | None = None,
) -> CustomerListPage:
    return await list_customers(
        session,
        skip=skip,
        limit=limit,
        sort=sort,
        search=search,
        seller_id=seller_id,
        industry=industry,
        closed=closed,
        from_date=from_date,
        to_date=to_date,
        uncategorized=uncategorized,
    )


@router.get("/{customer_id}")
async def get_customer_endpoint(
    customer_id: int,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> CustomerDetailResponse:
    detail = await get_customer_detail(session, customer_id)
    if detail is None:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id} no encontrado")
    return detail
