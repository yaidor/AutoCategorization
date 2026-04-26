from datetime import datetime
from enum import Enum, StrEnum
from typing import Any

from sqlalchemy import BigInteger, DateTime, Identity, Integer, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class JobStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


def _enum_values(enum_cls: type[Enum]) -> list[str]:
    return [member.value for member in enum_cls]


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    status: Mapped[JobStatus] = mapped_column(
        SAEnum(JobStatus, name="job_status", values_callable=_enum_values),
        nullable=False,
        server_default=JobStatus.QUEUED.value,
    )
    total: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    completed: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    failed: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    cached: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    errors: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False, server_default="[]")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
