"""厂家管理接口"""
import asyncio
import json
import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, require_role
from app.models.manufacturer import Manufacturer

logger = logging.getLogger(__name__)

router = APIRouter()


class ManufacturerCreate(BaseModel):
    name: str
    code: str
    api_base_url: str | None = None
    auth_config: dict | None = None
    sync_interval: int = 300


class ManufacturerUpdate(BaseModel):
    api_base_url: str | None = None
    auth_config: dict | None = None
    sync_interval: int | None = None
    is_active: bool | None = None


@router.get("")
async def list_manufacturers(db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    result = await db.execute(select(Manufacturer).order_by(Manufacturer.id))
    items = []
    for mfr in result.scalars().all():
        items.append({
            "id": mfr.id,
            "name": mfr.name,
            "code": mfr.code,
            "api_base_url": mfr.api_base_url,
            "sync_interval": mfr.sync_interval,
            "is_active": mfr.is_active,
            "last_sync_at": mfr.last_sync_at.isoformat() if mfr.last_sync_at else None,
        })
    return items


@router.post("")
async def create_manufacturer(data: ManufacturerCreate, db: AsyncSession = Depends(get_db), _=Depends(require_role("admin"))):
    existing = await db.scalar(select(Manufacturer).where((Manufacturer.code == data.code) | (Manufacturer.name == data.name)))
    if existing:
        raise HTTPException(status_code=400, detail="厂家名称或编码已存在")
    mfr = Manufacturer(
        name=data.name,
        code=data.code,
        api_base_url=data.api_base_url,
        auth_config=json.dumps(data.auth_config) if data.auth_config else None,
        sync_interval=data.sync_interval,
    )
    db.add(mfr)
    await db.commit()
    await db.refresh(mfr)
    return {"id": mfr.id, "name": mfr.name}


@router.put("/{mfr_id}")
async def update_manufacturer(mfr_id: int, data: ManufacturerUpdate, db: AsyncSession = Depends(get_db), _=Depends(require_role("admin"))):
    mfr = await db.get(Manufacturer, mfr_id)
    if not mfr:
        raise HTTPException(status_code=404, detail="厂家不存在")
    if data.api_base_url is not None:
        mfr.api_base_url = data.api_base_url
    if data.auth_config is not None:
        mfr.auth_config = json.dumps(data.auth_config)
    if data.sync_interval is not None:
        mfr.sync_interval = data.sync_interval
    if data.is_active is not None:
        mfr.is_active = data.is_active
    await db.commit()
    return {"ok": True}


@router.post("/{mfr_id}/sync")
async def sync_manufacturer(
    mfr_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_role("admin")),
):
    """触发单个厂家的完整同步（电站 + 设备 + 实时 + 日数据 + 告警）。

    在后台 asyncio 任务中执行同步，立即返回。
    """
    mfr = await db.get(Manufacturer, mfr_id)
    if not mfr:
        raise HTTPException(status_code=404, detail="厂家不存在")
    if not mfr.is_active:
        raise HTTPException(status_code=400, detail="该厂家已被禁用，请先启用")

    from app.services.sync_service import run_full_sync

    async def _runner(name: str):
        try:
            results = await run_full_sync()
            logger.info("厂家同步完成: %s, results=%s", name, results)
        except Exception as e:
            logger.error("厂家同步失败: %s, err=%s", name, e, exc_info=True)

    asyncio.create_task(_runner(mfr.name))
    return {
        "ok": True,
        "message": f"同步任务已提交: {mfr.name}，请稍后在同步日志中查看",
    }
