from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.enums import Industry
from app.schemas.metrics import (
    DiscoveryChannelMetric,
    IndustryMetric,
    ObjectionMetric,
    OverviewResponse,
    SellerMetric,
)
from app.services.metrics import (
    MetricsFilters,
    get_by_discovery_channel,
    get_by_industry,
    get_by_seller,
    get_overview,
    get_top_objections,
)

router = APIRouter(prefix="/metrics", tags=["metrics"])


def metrics_filters(
    from_date: Annotated[date | None, Query(alias="from")] = None,
    to_date: Annotated[date | None, Query(alias="to")] = None,
    seller_id: int | None = None,
    industry: Industry | None = None,
    closed: bool | None = None,
) -> MetricsFilters:
    return MetricsFilters(
        from_date=from_date,
        to_date=to_date,
        seller_id=seller_id,
        industry=industry,
        closed=closed,
    )


SessionDep = Annotated[AsyncSession, Depends(get_session)]
FiltersDep = Annotated[MetricsFilters, Depends(metrics_filters)]


@router.get("/overview")
async def overview_endpoint(session: SessionDep, filters: FiltersDep) -> OverviewResponse:
    return await get_overview(session, filters)


@router.get("/by-seller")
async def by_seller_endpoint(session: SessionDep, filters: FiltersDep) -> list[SellerMetric]:
    return await get_by_seller(session, filters)


@router.get("/by-industry")
async def by_industry_endpoint(session: SessionDep, filters: FiltersDep) -> list[IndustryMetric]:
    return await get_by_industry(session, filters)


@router.get("/objections")
async def objections_endpoint(
    session: SessionDep,
    filters: FiltersDep,
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
) -> list[ObjectionMetric]:
    return await get_top_objections(session, filters, limit=limit)


@router.get("/discovery-channels")
async def discovery_channels_endpoint(
    session: SessionDep, filters: FiltersDep
) -> list[DiscoveryChannelMetric]:
    return await get_by_discovery_channel(session, filters)
