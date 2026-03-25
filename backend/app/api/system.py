"""系统设置接口"""
import logging
from enum import Enum

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, require_role, hash_password
from app.models.user import User
from app.models.sync_log import SyncLog

logger = logging.getLogger(__name__)

router = APIRouter()


class UserCreate(BaseModel):
    username: str
    password: str
    display_name: str
    role: str = "viewer"
    phone: str | None = None
    email: str | None = None


@router.get("/users")
async def list_users(db: AsyncSession = Depends(get_db), _=Depends(require_role("admin"))):
    result = await db.execute(select(User).order_by(User.id))
    return [
        {
            "id": u.id,
            "username": u.username,
            "display_name": u.display_name,
            "role": u.role,
            "phone": u.phone,
            "is_active": u.is_active,
            "last_login_at": u.last_login_at.isoformat() if u.last_login_at else None,
        }
        for u in result.scalars().all()
    ]


@router.post("/users")
async def create_user(data: UserCreate, db: AsyncSession = Depends(get_db), _=Depends(require_role("admin"))):
    existing = await db.scalar(select(User).where(User.username == data.username))
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")
    user = User(
        username=data.username,
        password_hash=hash_password(data.password),
        display_name=data.display_name,
        role=data.role,
        phone=data.phone,
        email=data.email,
    )
    db.add(user)
    await db.commit()
    return {"id": user.id}


@router.get("/sync-logs")
async def list_sync_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    total = await db.scalar(select(func.count(SyncLog.id)))
    result = await db.execute(
        select(SyncLog).order_by(SyncLog.started_at.desc()).offset((page - 1) * page_size).limit(page_size)
    )
    return {
        "total": total,
        "items": [
            {
                "id": log.id,
                "manufacturer_code": log.manufacturer_code,
                "sync_type": log.sync_type,
                "status": log.status,
                "records_count": log.records_count,
                "error_message": log.error_message,
                "started_at": log.started_at.isoformat(),
                "finished_at": log.finished_at.isoformat() if log.finished_at else None,
            }
            for log in result.scalars().all()
        ],
    }


# ---------------------------------------------------------------------------
# 手动同步触发
# ---------------------------------------------------------------------------

class SyncType(str, Enum):
    full = "full"
    stations = "stations"
    realtime = "realtime"
    daily = "daily"
    devices = "devices"
    alarms = "alarms"


class SyncRequest(BaseModel):
    sync_type: SyncType = SyncType.full


@router.post("/sync")
async def trigger_manual_sync(
    body: SyncRequest = SyncRequest(),
    user=Depends(require_role("admin")),
):
    """手动触发数据同步（仅管理员）。

    将同步任务提交到 Celery 后台执行，立即返回 task_id。
    支持的 sync_type: full / stations / realtime / daily / devices / alarms
    """
    from app.tasks.sync_tasks import (
        run_full_sync_task,
        sync_all_stations_task,
        sync_all_realtime,
        sync_all_daily,
        sync_all_devices_task,
        sync_all_alarms,
    )

    task_map = {
        SyncType.full: run_full_sync_task,
        SyncType.stations: sync_all_stations_task,
        SyncType.realtime: sync_all_realtime,
        SyncType.daily: sync_all_daily,
        SyncType.devices: sync_all_devices_task,
        SyncType.alarms: sync_all_alarms,
    }

    task_func = task_map.get(body.sync_type)
    if task_func is None:
        raise HTTPException(status_code=400, detail=f"未知的同步类型: {body.sync_type}")

    try:
        result = task_func.delay()
        logger.info(
            "手动同步已触发: type=%s, task_id=%s, operator=%s",
            body.sync_type.value,
            result.id,
            user.username,
        )
        return {
            "ok": True,
            "message": f"同步任务已提交: {body.sync_type.value}",
            "task_id": result.id,
        }
    except Exception as exc:
        logger.error("提交同步任务失败: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"提交同步任务失败: {exc}")
