from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.categorization import Categorization
    from app.models.customer import Customer
    from app.models.seller import Seller


class Meeting(Base):
    __tablename__ = "meetings"

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    customer_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False
    )
    seller_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("sellers.id", ondelete="RESTRICT"), nullable=False
    )
    meeting_date: Mapped[date] = mapped_column(Date, nullable=False)
    closed: Mapped[bool] = mapped_column(Boolean, server_default="false", nullable=False)
    transcript: Mapped[str] = mapped_column(Text, nullable=False)
    transcript_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    customer: Mapped["Customer"] = relationship(back_populates="meetings")
    seller: Mapped["Seller"] = relationship(back_populates="meetings")
    categorizations: Mapped[list["Categorization"]] = relationship(
        back_populates="meeting", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_meetings_seller_date", "seller_id", "meeting_date"),
        Index("ix_meetings_closed", "closed"),
    )
