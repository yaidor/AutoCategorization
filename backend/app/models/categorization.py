from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Identity,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
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

if TYPE_CHECKING:
    from app.models.meeting import Meeting


def _enum_values(enum_cls: type[Enum]) -> list[str]:
    return [member.value for member in enum_cls]


class Categorization(Base):
    __tablename__ = "categorizations"

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    meeting_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False
    )
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    prompt_version: Mapped[str] = mapped_column(String(20), nullable=False)
    raw_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)

    industry: Mapped[Industry] = mapped_column(
        SAEnum(Industry, name="industry", values_callable=_enum_values),
        nullable=False,
    )
    use_case: Mapped[UseCase] = mapped_column(
        SAEnum(UseCase, name="use_case", values_callable=_enum_values),
        nullable=False,
    )
    interest_level: Mapped[int] = mapped_column(Integer, nullable=False)
    sentiment: Mapped[float] = mapped_column(Float, nullable=False)
    urgency: Mapped[Urgency] = mapped_column(
        SAEnum(Urgency, name="urgency", values_callable=_enum_values),
        nullable=False,
    )

    volume_amount: Mapped[int | None] = mapped_column(Integer, nullable=True)
    volume_period: Mapped[VolumePeriod | None] = mapped_column(
        SAEnum(VolumePeriod, name="volume_period", values_callable=_enum_values),
        nullable=True,
    )

    discovery_channel: Mapped[DiscoveryChannel] = mapped_column(
        SAEnum(DiscoveryChannel, name="discovery_channel", values_callable=_enum_values),
        nullable=False,
    )
    integration_required: Mapped[bool] = mapped_column(Boolean, nullable=False)
    systems_mentioned: Mapped[list[str]] = mapped_column(
        ARRAY(Text), server_default="{}", nullable=False
    )
    competitors_mentioned: Mapped[list[str]] = mapped_column(
        ARRAY(Text), server_default="{}", nullable=False
    )
    main_objection: Mapped[str | None] = mapped_column(Text, nullable=True)
    personalization_concern: Mapped[PersonalizationConcern] = mapped_column(
        SAEnum(
            PersonalizationConcern,
            name="personalization_concern",
            values_callable=_enum_values,
        ),
        nullable=False,
    )
    data_sensitivity: Mapped[DataSensitivity] = mapped_column(
        SAEnum(DataSensitivity, name="data_sensitivity", values_callable=_enum_values),
        nullable=False,
    )
    close_probability: Mapped[float] = mapped_column(Float, nullable=False)
    customer_segment: Mapped[CustomerSegment] = mapped_column(
        SAEnum(CustomerSegment, name="customer_segment", values_callable=_enum_values),
        nullable=False,
    )
    key_topics: Mapped[list[str]] = mapped_column(ARRAY(Text), server_default="{}", nullable=False)
    summary_es: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    meeting: Mapped["Meeting"] = relationship(back_populates="categorizations")

    __table_args__ = (
        UniqueConstraint(
            "meeting_id",
            "prompt_version",
            "model",
            name="uq_categorizations_meeting_prompt_model",
        ),
        Index("ix_categorizations_industry", "industry"),
        Index(
            "ix_categorizations_key_topics",
            "key_topics",
            postgresql_using="gin",
        ),
    )
