from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import Industry
from app.schemas.categorization import CategorizationResponse


class CustomerListItem(BaseModel):
    customer_id: int
    customer_name: str
    customer_email: str | None
    customer_phone: str | None
    seller_id: int
    seller_name: str
    meeting_id: int
    meeting_date: date
    closed: bool
    industry: Industry | None
    close_probability: float | None
    has_categorization: bool


class CustomerListPage(BaseModel):
    items: list[CustomerListItem]
    total: int
    skip: int
    limit: int


class SellerSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class MeetingDetailResponse(BaseModel):
    id: int
    meeting_date: date
    closed: bool
    transcript: str
    transcript_hash: str
    created_at: datetime
    categorization: CategorizationResponse | None


class CustomerDetailResponse(BaseModel):
    id: int
    name: str
    email: str | None
    phone: str | None
    created_at: datetime
    seller: SellerSummary
    meetings: list[MeetingDetailResponse]
