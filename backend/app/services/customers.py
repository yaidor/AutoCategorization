from datetime import date
from typing import Literal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Categorization, Customer, Meeting, Seller
from app.models.enums import Industry
from app.schemas.categorization import CategorizationResponse
from app.schemas.customers import (
    CustomerDetailResponse,
    CustomerListItem,
    CustomerListPage,
    MeetingDetailResponse,
    SellerSummary,
)
from app.services.llm.factory import get_llm_provider
from app.services.llm.prompt import PROMPT_VERSION

SortField = Literal[
    "meeting_date_desc",
    "meeting_date_asc",
    "customer_name_asc",
    "customer_name_desc",
]


async def list_customers(
    session: AsyncSession,
    *,
    skip: int = 0,
    limit: int = 20,
    sort: SortField = "meeting_date_desc",
    search: str | None = None,
    seller_id: int | None = None,
    industry: Industry | None = None,
    closed: bool | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
) -> CustomerListPage:
    provider = get_llm_provider()
    model_filter = provider.model

    base = (
        select(
            Customer.id.label("customer_id"),
            Customer.name.label("customer_name"),
            Customer.email.label("customer_email"),
            Customer.phone.label("customer_phone"),
            Seller.id.label("seller_id"),
            Seller.name.label("seller_name"),
            Meeting.id.label("meeting_id"),
            Meeting.meeting_date,
            Meeting.closed,
            Categorization.industry,
            Categorization.close_probability,
            Categorization.id.is_not(None).label("has_categorization"),
        )
        .select_from(Customer)
        .join(Seller, Seller.id == Customer.seller_id)
        .join(Meeting, Meeting.customer_id == Customer.id)
        .outerjoin(
            Categorization,
            (Categorization.meeting_id == Meeting.id)
            & (Categorization.prompt_version == PROMPT_VERSION)
            & (Categorization.model == model_filter),
        )
    )

    if search:
        base = base.where(Customer.name.ilike(f"%{search}%"))
    if seller_id is not None:
        base = base.where(Customer.seller_id == seller_id)
    if industry is not None:
        base = base.where(Categorization.industry == industry)
    if closed is not None:
        base = base.where(Meeting.closed.is_(closed))
    if from_date is not None:
        base = base.where(Meeting.meeting_date >= from_date)
    if to_date is not None:
        base = base.where(Meeting.meeting_date <= to_date)

    count_stmt = select(func.count()).select_from(base.subquery())
    total = (await session.execute(count_stmt)).scalar_one()

    if sort == "meeting_date_desc":
        base = base.order_by(Meeting.meeting_date.desc(), Customer.id.desc())
    elif sort == "meeting_date_asc":
        base = base.order_by(Meeting.meeting_date.asc(), Customer.id.asc())
    elif sort == "customer_name_asc":
        base = base.order_by(Customer.name.asc())
    elif sort == "customer_name_desc":
        base = base.order_by(Customer.name.desc())

    base = base.offset(skip).limit(limit)
    rows = (await session.execute(base)).all()

    items = [
        CustomerListItem(
            customer_id=row.customer_id,
            customer_name=row.customer_name,
            customer_email=row.customer_email,
            customer_phone=row.customer_phone,
            seller_id=row.seller_id,
            seller_name=row.seller_name,
            meeting_id=row.meeting_id,
            meeting_date=row.meeting_date,
            closed=row.closed,
            industry=row.industry,
            close_probability=row.close_probability,
            has_categorization=bool(row.has_categorization),
        )
        for row in rows
    ]

    return CustomerListPage(items=items, total=total, skip=skip, limit=limit)


async def get_customer_detail(
    session: AsyncSession, customer_id: int
) -> CustomerDetailResponse | None:
    stmt = (
        select(Customer)
        .options(
            selectinload(Customer.seller),
            selectinload(Customer.meetings).selectinload(Meeting.categorizations),
        )
        .where(Customer.id == customer_id)
    )
    customer = (await session.execute(stmt)).scalar_one_or_none()
    if customer is None:
        return None

    provider = get_llm_provider()

    meetings_response: list[MeetingDetailResponse] = []
    sorted_meetings = sorted(customer.meetings, key=lambda m: m.meeting_date, reverse=True)
    for meeting in sorted_meetings:
        cat = next(
            (
                c
                for c in meeting.categorizations
                if c.prompt_version == PROMPT_VERSION and c.model == provider.model
            ),
            None,
        )
        cat_response = None
        if cat is not None:
            cat_response = CategorizationResponse.model_validate(cat).model_copy(
                update={"cached": True}
            )
        meetings_response.append(
            MeetingDetailResponse(
                id=meeting.id,
                meeting_date=meeting.meeting_date,
                closed=meeting.closed,
                transcript=meeting.transcript,
                transcript_hash=meeting.transcript_hash,
                created_at=meeting.created_at,
                categorization=cat_response,
            )
        )

    return CustomerDetailResponse(
        id=customer.id,
        name=customer.name,
        email=customer.email,
        phone=customer.phone,
        created_at=customer.created_at,
        seller=SellerSummary.model_validate(customer.seller),
        meetings=meetings_response,
    )
