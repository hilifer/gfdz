"""End-to-end full sync runner — used by CI to verify adapters & sync logic.

Steps:
  1. Create DB tables.
  2. Seed default manufacturers (huawei / sungrow / aiswei / solis).
  3. Run run_full_sync().
  4. Print per-manufacturer results and exit non-zero if every manufacturer failed
     to fetch any stations.
"""
from __future__ import annotations

import asyncio
import json
import logging
import sys
from typing import Any

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("run_full_sync")


async def main() -> int:
    from app.database import Base, async_session, engine
    from app.services.init_data import init_default_data
    from app.services.sync_service import run_full_sync
    from sqlalchemy import select, func
    from app.models.station import Station
    from app.models.sync_log import SyncLog

    logger.info("Creating tables ...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("Seeding default manufacturers / users ...")
    await init_default_data()

    logger.info("Running full sync ...")
    results = await run_full_sync()

    logger.info("Sync results: %s", json.dumps(_summarize(results), ensure_ascii=False, indent=2))

    async with async_session() as db:
        station_count = await db.scalar(select(func.count(Station.id))) or 0
        logger.info("Total stations in DB: %d", station_count)

        log_rows = await db.execute(
            select(SyncLog).order_by(SyncLog.id.desc()).limit(50)
        )
        logger.info("--- Recent sync logs ---")
        for row in log_rows.scalars().all():
            logger.info(
                "  [%s] mfr=%s status=%s records=%s err=%s",
                row.sync_type, row.manufacturer_code, row.status,
                row.records_count, (row.error_message or "")[:200],
            )

    stations_summary = results.get("stations") or {}
    if stations_summary.get("created", 0) + stations_summary.get("updated", 0) == 0:
        logger.error("No stations were created or updated by any manufacturer; failing CI.")
        return 1

    return 0


def _summarize(results: dict[str, Any]) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    for k, v in results.items():
        if isinstance(v, dict):
            summary[k] = {
                kk: (vv if not isinstance(vv, list) else f"{len(vv)} entries (showing 3): {vv[:3]}")
                for kk, vv in v.items()
            }
        else:
            summary[k] = v
    return summary


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
