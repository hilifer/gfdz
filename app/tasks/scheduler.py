"""定时任务调度器"""
import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select

from config import settings
from app.database import async_session
from app.models.power_station import PowerStation
from app.services.sync_service import sync_single_station

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()


async def scheduled_sync_all():
    """定时同步所有活跃电站"""
    logger.info("开始定时同步所有电站数据...")
    async with async_session() as db:
        result = await db.execute(
            select(PowerStation).where(PowerStation.is_active == True)
        )
        stations = result.scalars().all()

        success = 0
        failed = 0
        for station in stations:
            r = await sync_single_station(station.id, db)
            if r.get("success"):
                success += 1
            else:
                failed += 1
                logger.warning(f"同步电站[{station.name}]失败: {r.get('error')}")

    logger.info(f"定时同步完成: 成功{success}, 失败{failed}, 共{len(stations)}")


def start_scheduler():
    """启动定时调度器"""
    scheduler.add_job(
        scheduled_sync_all,
        "interval",
        minutes=settings.SYNC_INTERVAL_MINUTES,
        id="sync_all_stations",
        replace_existing=True,
    )
    scheduler.start()
    logger.info(f"定时调度器已启动，同步间隔: {settings.SYNC_INTERVAL_MINUTES}分钟")


def stop_scheduler():
    """停止调度器"""
    if scheduler.running:
        scheduler.shutdown()
