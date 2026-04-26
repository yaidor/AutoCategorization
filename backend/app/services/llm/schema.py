from pydantic import BaseModel, ConfigDict, Field

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


class EstimatedVolume(BaseModel):
    model_config = ConfigDict(extra="ignore")

    amount: int | None = None
    period: VolumePeriod | None = None


class CategorizationResult(BaseModel):
    model_config = ConfigDict(extra="ignore")

    industry: Industry
    use_case: UseCase
    interest_level: int = Field(ge=1, le=5)
    sentiment: float = Field(ge=-1.0, le=1.0)
    urgency: Urgency
    estimated_volume: EstimatedVolume
    discovery_channel: DiscoveryChannel
    integration_required: bool
    systems_mentioned: list[str]
    main_objection: str | None = None
    competitors_mentioned: list[str]
    personalization_concern: PersonalizationConcern
    data_sensitivity: DataSensitivity
    close_probability: float = Field(ge=0.0, le=1.0)
    customer_segment: CustomerSegment
    key_topics: list[str]
    summary_es: str = Field(min_length=1)
