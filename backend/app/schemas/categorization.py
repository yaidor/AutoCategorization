from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import (
    CustomerSegment,
    DataSensitivity,
    DiscoveryChannel,
    Industry,
    PersonalizationConcern,
    Urgency,
    UseCase,
    VolumePeriod,
)
from app.models.job import JobStatus


class CategorizationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    meeting_id: int
    provider: str
    model: str
    prompt_version: str
    industry: Industry
    use_case: UseCase
    interest_level: int
    sentiment: float
    urgency: Urgency
    volume_amount: int | None
    volume_period: VolumePeriod | None
    discovery_channel: DiscoveryChannel
    integration_required: bool
    systems_mentioned: list[str]
    main_objection: str | None
    competitors_mentioned: list[str]
    personalization_concern: PersonalizationConcern
    data_sensitivity: DataSensitivity
    close_probability: float
    customer_segment: CustomerSegment
    key_topics: list[str]
    summary_es: str
    cached: bool = False
    created_at: datetime


class JobError(BaseModel):
    meeting_id: int
    error: str


class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: JobStatus
    total: int
    completed: int
    failed: int
    cached: int
    errors: list[JobError]
    created_at: datetime
    updated_at: datetime
