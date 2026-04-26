from pydantic import BaseModel

from app.models.enums import DiscoveryChannel, Industry


class OverviewResponse(BaseModel):
    total_meetings: int
    closed_meetings: int
    close_rate: float
    avg_sentiment: float | None
    avg_close_probability: float | None
    top_industry: Industry | None
    top_discovery_channel: DiscoveryChannel | None


class SellerMetric(BaseModel):
    seller_id: int
    seller_name: str
    total_meetings: int
    closed_meetings: int
    close_rate: float
    avg_sentiment: float
    avg_interest_level: float
    avg_close_probability: float


class IndustryMetric(BaseModel):
    industry: Industry
    total_meetings: int
    closed_meetings: int
    close_rate: float
    avg_close_probability: float


class ObjectionMetric(BaseModel):
    objection: str
    count: int
    frequency_pct: float


class DiscoveryChannelMetric(BaseModel):
    discovery_channel: DiscoveryChannel
    total_meetings: int
    closed_meetings: int
    close_rate: float
