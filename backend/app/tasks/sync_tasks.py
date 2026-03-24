"""同步任务"""
import logging

from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task
def sync_all_realtime():
    """同步所有电站实时数据"""
    logger.info("开始同步实时数据...")
    # TODO: 遍历所有厂家，调用适配器同步
    logger.info("实时数据同步完成")


@celery_app.task
def sync_all_daily():
    """同步所有电站日数据"""
    logger.info("开始同步日数据...")
    logger.info("日数据同步完成")


@celery_app.task
def sync_all_alarms():
    """同步所有电站告警"""
    logger.info("开始同步告警...")
    logger.info("告警同步完成")
