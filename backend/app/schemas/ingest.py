from datetime import date

from pydantic import BaseModel, Field, field_validator


class MeetingRow(BaseModel):
    name: str = Field(min_length=1)
    email: str | None = None
    phone: str | None = None
    meeting_date: date
    seller_name: str = Field(min_length=1)
    closed: bool
    transcript: str = Field(min_length=1)

    @field_validator("email", mode="before")
    @classmethod
    def _empty_email_to_none(cls, value: object) -> object:
        if isinstance(value, str) and value.strip() == "":
            return None
        return value

    @field_validator("phone", mode="before")
    @classmethod
    def _phone_to_string(cls, value: object) -> object:
        if value is None:
            return None
        if isinstance(value, str) and value.strip() == "":
            return None
        return str(value).strip()


class IngestError(BaseModel):
    row: int
    field: str | None = None
    message: str


class IngestSummary(BaseModel):
    total_rows: int
    inserted: int
    skipped_duplicates: int
    errors: list[IngestError] = Field(default_factory=list)
    new_sellers: list[str] = Field(default_factory=list)
