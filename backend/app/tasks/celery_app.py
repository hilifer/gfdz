"""Celery 应用配置"""
from celery import Celery
from celery.schedules import crontab

from app.config import settings

celery_app = Celery("gfdz", broker=settings.REDIS_URL, backend=settings.REDIS_URL)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=False,
    beat_schedule={
        # 每5分钟同步实时数据
        "sync-realtime": {
            "task": "app.tasks.sync_tasks.sync_all_realtime",
            "schedule": 300,
        },
        # 每天凌晨1点同步日数据
        "sync-daily": {
            "task": "app.tasks.sync_tasks.sync_all_daily",
            "schedule": crontab(hour=1, minute=0),
        },
        # 每10分钟同步告警
        "sync-alarms": {
            "task": "app.tasks.sync_tasks.sync_all_alarms",
            "schedule": 600,
        },
    },
)

celery_app.autodiscover_tasks(["app.tasks"])
