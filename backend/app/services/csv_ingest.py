import csv
import hashlib
import io
import unicodedata
from collections.abc import Iterable

import structlog
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.cli.seed import SELLERS as KNOWN_SELLERS
from app.models import Customer, Meeting, Seller
from app.schemas.ingest import IngestError, IngestSummary, MeetingRow

log = structlog.get_logger()


HEADER_MAP = {
    "nombre": "name",
    "correo_electronico": "email",
    "numero_de_telefono": "phone",
    "fecha_de_la_reunion": "meeting_date",
    "vendedor_asignado": "seller_name",
    "closed": "closed",
    "transcripcion": "transcript",
}

REQUIRED_FIELDS = set(HEADER_MAP.values())


def _normalize_header(header: str) -> str:
    nfd = unicodedata.normalize("NFD", header)
    no_accents = "".join(c for c in nfd if not unicodedata.combining(c))
    return no_accents.strip().lower().replace(" ", "_")


def _hash_transcript(transcript: str) -> str:
    return hashlib.sha256(transcript.encode("utf-8")).hexdigest()


def parse_csv_bytes(data: bytes) -> tuple[list[MeetingRow], list[IngestError]]:
    text = data.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))

    if not reader.fieldnames:
        return [], [IngestError(row=0, field=None, message="CSV vacío o sin headers")]

    field_mapping: dict[str, str] = {}
    for original in reader.fieldnames:
        normalized = _normalize_header(original)
        target = HEADER_MAP.get(normalized)
        if target is not None:
            field_mapping[original] = target

    missing = REQUIRED_FIELDS - set(field_mapping.values())
    if missing:
        return [], [
            IngestError(
                row=0,
                field=None,
                message=f"Headers faltantes: {sorted(missing)}",
            )
        ]

    valid: list[MeetingRow] = []
    errors: list[IngestError] = []

    for idx, raw_row in enumerate(reader, start=2):
        translated = {field_mapping[k]: v for k, v in raw_row.items() if k in field_mapping}
        try:
            valid.append(MeetingRow.model_validate(translated))
        except ValidationError as exc:
            for err in exc.errors():
                field = err["loc"][0] if err["loc"] else None
                errors.append(
                    IngestError(
                        row=idx,
                        field=str(field) if field else None,
                        message=err["msg"],
                    )
                )

    return valid, errors


async def _upsert_sellers(
    session: AsyncSession, names: Iterable[str]
) -> tuple[dict[str, int], list[str]]:
    unique_names = sorted(set(names))
    if not unique_names:
        return {}, []

    existing_stmt = select(Seller).where(Seller.name.in_(unique_names))
    result = await session.execute(existing_stmt)
    existing: dict[str, int] = {s.name: s.id for s in result.scalars().all()}

    missing = [n for n in unique_names if n not in existing]
    new_unexpected: list[str] = []

    if missing:
        insert_stmt = (
            pg_insert(Seller)
            .values([{"name": n} for n in missing])
            .on_conflict_do_nothing(index_elements=["name"])
            .returning(Seller.id, Seller.name)
        )
        insert_result = await session.execute(insert_stmt)
        for sid, sname in insert_result.all():
            existing[sname] = sid
            if sname not in KNOWN_SELLERS:
                new_unexpected.append(sname)
                log.warning("seller_unexpected", name=sname)

    return existing, new_unexpected


async def _get_or_create_customer(
    session: AsyncSession,
    name: str,
    email: str | None,
    phone: str | None,
    seller_id: int,
) -> int:
    stmt = select(Customer).where(Customer.name == name, Customer.seller_id == seller_id)
    existing = (await session.execute(stmt)).scalar_one_or_none()
    if existing is not None:
        return existing.id

    customer = Customer(name=name, email=email, phone=phone, seller_id=seller_id)
    session.add(customer)
    await session.flush()
    return customer.id


async def persist_rows(rows: list[MeetingRow], session: AsyncSession) -> tuple[int, int, list[str]]:
    if not rows:
        return 0, 0, []

    seller_ids, new_sellers = await _upsert_sellers(session, (row.seller_name for row in rows))

    # Dedup por hash dentro del batch (último gana, igual que ON CONFLICT real).
    by_hash: dict[str, MeetingRow] = {}
    in_batch_dups = 0
    for row in rows:
        thash = _hash_transcript(row.transcript)
        if thash in by_hash:
            in_batch_dups += 1
            continue
        by_hash[thash] = row

    existing_hashes_stmt = select(Meeting.transcript_hash).where(
        Meeting.transcript_hash.in_(by_hash.keys())
    )
    existing_hashes: set[str] = set((await session.execute(existing_hashes_stmt)).scalars().all())

    inserted = 0
    skipped_db = 0

    for thash, row in by_hash.items():
        if thash in existing_hashes:
            skipped_db += 1
            continue

        seller_id = seller_ids[row.seller_name]
        customer_id = await _get_or_create_customer(
            session, row.name, row.email, row.phone, seller_id
        )
        meeting = Meeting(
            customer_id=customer_id,
            seller_id=seller_id,
            meeting_date=row.meeting_date,
            closed=row.closed,
            transcript=row.transcript,
            transcript_hash=thash,
        )
        session.add(meeting)
        inserted += 1

    await session.commit()
    return inserted, skipped_db + in_batch_dups, new_sellers


async def ingest_csv(data: bytes, session: AsyncSession) -> IngestSummary:
    rows, errors = parse_csv_bytes(data)
    inserted, skipped, new_sellers = await persist_rows(rows, session)
    return IngestSummary(
        total_rows=len(rows) + len(errors),
        inserted=inserted,
        skipped_duplicates=skipped,
        errors=errors,
        new_sellers=new_sellers,
    )
