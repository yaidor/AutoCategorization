import asyncio

import structlog
from sqlalchemy.dialects.postgresql import insert

from app.core.config import settings
from app.core.logging import configure_logging
from app.db.session import async_session_factory, engine
from app.models import Seller

SELLERS = ["Toro", "Puma", "Zorro", "Boa", "Tiburón"]


async def seed_sellers() -> int:
    log = structlog.get_logger()
    stmt = (
        insert(Seller)
        .values([{"name": name} for name in SELLERS])
        .on_conflict_do_nothing(index_elements=["name"])
        .returning(Seller.id)
    )
    async with async_session_factory() as session:
        result = await session.execute(stmt)
        inserted_ids = list(result.scalars().all())
        await session.commit()

    log.info(
        "sellers_seeded",
        inserted=len(inserted_ids),
        skipped=len(SELLERS) - len(inserted_ids),
        names=SELLERS,
    )
    return len(inserted_ids)


async def main() -> None:
    configure_logging(settings.log_level, settings.environment)
    try:
        await seed_sellers()
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
