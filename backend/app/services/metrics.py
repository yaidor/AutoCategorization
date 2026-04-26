from dataclasses import dataclass
from datetime import date

from sqlalchemy import Select, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Categorization, Meeting, Seller
from app.models.enums import Industry
from app.schemas.metrics import (
    DiscoveryChannelMetric,
    IndustryMetric,
    ObjectionMetric,
    OverviewResponse,
    SellerMetric,
)


@dataclass(frozen=True, slots=True)
class MetricsFilters:
    from_date: date | None = None
    to_date: date | None = None
    seller_id: int | None = None
    industry: Industry | None = None
    closed: bool | None = None


def _apply_filters(stmt: Select, filters: MetricsFilters) -> Select:
    if filters.from_date is not None:
        stmt = stmt.where(Meeting.meeting_date >= filters.from_date)
    if filters.to_date is not None:
        stmt = stmt.where(Meeting.meeting_date <= filters.to_date)
    if filters.seller_id is not None:
        stmt = stmt.where(Meeting.seller_id == filters.seller_id)
    if filters.industry is not None:
        stmt = stmt.where(Categorization.industry == filters.industry)
    if filters.closed is not None:
        stmt = stmt.where(Meeting.closed.is_(filters.closed))
    return stmt


async def get_overview(session: AsyncSession, filters: MetricsFilters) -> OverviewResponse:
    base = (
        select(
            func.count(Categorization.id).label("total"),
            func.count().filter(Meeting.closed.is_(True)).label("closed_count"),
            func.avg(Categorization.sentiment).label("avg_sentiment"),
            func.avg(Categorization.close_probability).label("avg_close_prob"),
        )
        .select_from(Categorization)
        .join(Meeting, Meeting.id == Categorization.meeting_id)
    )
    base = _apply_filters(base, filters)
    row = (await session.execute(base)).one()

    total = row.total or 0
    closed = row.closed_count or 0
    close_rate = (closed / total) if total > 0 else 0.0

    top_ind_stmt = (
        select(Categorization.industry, func.count().label("n"))
        .select_from(Categorization)
        .join(Meeting, Meeting.id == Categorization.meeting_id)
        .group_by(Categorization.industry)
        .order_by(desc("n"))
        .limit(1)
    )
    top_ind_stmt = _apply_filters(top_ind_stmt, filters)
    top_ind = (await session.execute(top_ind_stmt)).first()

    top_dc_stmt = (
        select(Categorization.discovery_channel, func.count().label("n"))
        .select_from(Categorization)
        .join(Meeting, Meeting.id == Categorization.meeting_id)
        .group_by(Categorization.discovery_channel)
        .order_by(desc("n"))
        .limit(1)
    )
    top_dc_stmt = _apply_filters(top_dc_stmt, filters)
    top_dc = (await session.execute(top_dc_stmt)).first()

    return OverviewResponse(
        total_meetings=total,
        closed_meetings=closed,
        close_rate=round(close_rate, 4),
        avg_sentiment=round(row.avg_sentiment, 3) if row.avg_sentiment is not None else None,
        avg_close_probability=(
            round(row.avg_close_prob, 3) if row.avg_close_prob is not None else None
        ),
        top_industry=top_ind.industry if top_ind else None,
        top_discovery_channel=top_dc.discovery_channel if top_dc else None,
    )


async def get_by_seller(session: AsyncSession, filters: MetricsFilters) -> list[SellerMetric]:
    stmt = (
        select(
            Seller.id,
            Seller.name,
            func.count(Categorization.id).label("total"),
            func.count().filter(Meeting.closed.is_(True)).label("closed_count"),
            func.avg(Categorization.sentiment).label("avg_sentiment"),
            func.avg(Categorization.interest_level).label("avg_interest"),
            func.avg(Categorization.close_probability).label("avg_close_prob"),
        )
        .select_from(Categorization)
        .join(Meeting, Meeting.id == Categorization.meeting_id)
        .join(Seller, Seller.id == Meeting.seller_id)
        .group_by(Seller.id, Seller.name)
        .having(func.count(Categorization.id) > 0)
        .order_by(desc("total"))
    )
    stmt = _apply_filters(stmt, filters)
    rows = (await session.execute(stmt)).all()

    return [
        SellerMetric(
            seller_id=r.id,
            seller_name=r.name,
            total_meetings=r.total,
            closed_meetings=r.closed_count or 0,
            close_rate=round((r.closed_count or 0) / r.total, 4),
            avg_sentiment=round(r.avg_sentiment, 3),
            avg_interest_level=round(r.avg_interest, 2),
            avg_close_probability=round(r.avg_close_prob, 3),
        )
        for r in rows
    ]


async def get_by_industry(session: AsyncSession, filters: MetricsFilters) -> list[IndustryMetric]:
    stmt = (
        select(
            Categorization.industry,
            func.count(Categorization.id).label("total"),
            func.count().filter(Meeting.closed.is_(True)).label("closed_count"),
            func.avg(Categorization.close_probability).label("avg_close_prob"),
        )
        .select_from(Categorization)
        .join(Meeting, Meeting.id == Categorization.meeting_id)
        .group_by(Categorization.industry)
        .having(func.count(Categorization.id) > 0)
        .order_by(desc("total"))
    )
    stmt = _apply_filters(stmt, filters)
    rows = (await session.execute(stmt)).all()

    return [
        IndustryMetric(
            industry=r.industry,
            total_meetings=r.total,
            closed_meetings=r.closed_count or 0,
            close_rate=round((r.closed_count or 0) / r.total, 4),
            avg_close_probability=round(r.avg_close_prob, 3),
        )
        for r in rows
    ]


async def get_top_objections(
    session: AsyncSession, filters: MetricsFilters, limit: int
) -> list[ObjectionMetric]:
    total_stmt = (
        select(func.count(Categorization.id))
        .select_from(Categorization)
        .join(Meeting, Meeting.id == Categorization.meeting_id)
        .where(Categorization.main_objection.is_not(None))
    )
    total_stmt = _apply_filters(total_stmt, filters)
    total_with_obj = (await session.execute(total_stmt)).scalar_one()

    if total_with_obj == 0:
        return []

    stmt = (
        select(
            Categorization.main_objection,
            func.count().label("n"),
        )
        .select_from(Categorization)
        .join(Meeting, Meeting.id == Categorization.meeting_id)
        .where(Categorization.main_objection.is_not(None))
        .group_by(Categorization.main_objection)
        .order_by(desc("n"))
        .limit(limit)
    )
    stmt = _apply_filters(stmt, filters)
    rows = (await session.execute(stmt)).all()

    return [
        ObjectionMetric(
            objection=r.main_objection,
            count=r.n,
            frequency_pct=round(r.n / total_with_obj * 100, 2),
        )
        for r in rows
    ]


async def get_by_discovery_channel(
    session: AsyncSession, filters: MetricsFilters
) -> list[DiscoveryChannelMetric]:
    stmt = (
        select(
            Categorization.discovery_channel,
            func.count(Categorization.id).label("total"),
            func.count().filter(Meeting.closed.is_(True)).label("closed_count"),
        )
        .select_from(Categorization)
        .join(Meeting, Meeting.id == Categorization.meeting_id)
        .group_by(Categorization.discovery_channel)
        .having(func.count(Categorization.id) > 0)
        .order_by(desc("total"))
    )
    stmt = _apply_filters(stmt, filters)
    rows = (await session.execute(stmt)).all()

    return [
        DiscoveryChannelMetric(
            discovery_channel=r.discovery_channel,
            total_meetings=r.total,
            closed_meetings=r.closed_count or 0,
            close_rate=round((r.closed_count or 0) / r.total, 4),
        )
        for r in rows
    ]
