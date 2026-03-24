"""同步任务 - Celery 定时任务调用 async 同步服务"""
import asyncio
import logging

from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


def _run_async(coro):
    """在 Celery 同步 worker 中运行异步协程."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            raise RuntimeError
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


@celery_app.task(bind=True, max_retries=2, default_retry_delay=60)
def sync_all_realtime(self):
    """同步所有电站实时数据"""
    logger.info("开始同步实时数据...")
    try:
        from app.services.sync_service import sync_realtime_data
        result = _run_async(sync_realtime_data())
        logger.info("实时数据同步完成: %s", result)
        return result
    except Exception as exc:
        logger.error("实时数据同步失败: %s", exc, exc_info=True)
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=2, default_retry_delay=60)
def sync_all_daily(self):
    """同步所有电站日数据"""
    logger.info("开始同步日数据...")
    try:
        from app.services.sync_service import sync_daily_data
        result = _run_async(sync_daily_data())
        logger.info("日数据同步完成: %s", result)
        return result
    except Exception as exc:
        logger.error("日数据同步失败: %s", exc, exc_info=True)
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=2, default_retry_delay=60)
def sync_all_alarms(self):
    """同步所有电站告警"""
    logger.info("开始同步告警...")
    try:
        from app.services.sync_service import sync_alarms
        result = _run_async(sync_alarms())
        logger.info("告警同步完成: %s", result)
        return result
    except Exception as exc:
        logger.error("告警同步失败: %s", exc, exc_info=True)
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=1, default_retry_delay=120)
def sync_all_stations_task(self):
    """同步所有电站列表"""
    logger.info("开始同步电站列表...")
    try:
        from app.services.sync_service import sync_all_stations
        result = _run_async(sync_all_stations())
        logger.info("电站列表同步完成: %s", result)
        return result
    except Exception as exc:
        logger.error("电站列表同步失败: %s", exc, exc_info=True)
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=1, default_retry_delay=120)
def sync_all_devices_task(self):
    """同步所有设备列表"""
    logger.info("开始同步设备列表...")
    try:
        from app.services.sync_service import sync_devices
        result = _run_async(sync_devices())
        logger.info("设备列表同步完成: %s", result)
        return result
    except Exception as exc:
        logger.error("设备列表同步失败: %s", exc, exc_info=True)
        raise self.retry(exc=exc)


@celery_app.task
def run_full_sync_task():
    """完整同步（手动触发）"""
    logger.info("开始完整同步（手动触发）...")
    try:
        from app.services.sync_service import run_full_sync
        result = _run_async(run_full_sync())
        logger.info("完整同步完成: %s", result)
        return result
    except Exception as exc:
        logger.error("完整同步失败: %s", exc, exc_info=True)
        raise
