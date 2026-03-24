"""设备管理接口"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.device import Device
from app.models.device_data import DeviceData
from app.models.station import Station

router = APIRouter()


@router.get("")
async def list_devices(
    station_id: int | None = None,
    device_type: str | None = None,
    status: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    """设备列表"""
    query = select(Device, Station.name.label("station_name")).join(Station)

    if station_id:
        query = query.where(Device.station_id == station_id)
    if device_type:
        query = query.where(Device.device_type == device_type)
    if status:
        query = query.where(Device.status == status)

    total = await db.scalar(
        select(func.count(Device.id))
        .where(Device.station_id == station_id if station_id else True)
    )

    result = await db.execute(query.offset((page - 1) * page_size).limit(page_size))

    items = []
    for device, station_name in result.all():
        items.append({
            "id": device.id,
            "device_code": device.device_code,
            "device_name": device.device_name,
            "device_type": device.device_type,
            "station_name": station_name,
            "station_id": device.station_id,
            "brand": device.brand,
            "model": device.model,
            "rated_power": device.rated_power,
            "status": device.status,
            "last_data_at": device.last_data_at.isoformat() if device.last_data_at else None,
        })

    return {"total": total, "items": items, "page": page, "page_size": page_size}


@router.get("/{device_id}")
async def get_device(device_id: int, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    device = await db.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")

    # 最新一条数据
    latest = await db.scalar(
        select(DeviceData)
        .where(DeviceData.device_id == device_id)
        .order_by(DeviceData.timestamp.desc())
        .limit(1)
    )

    return {
        "id": device.id,
        "device_code": device.device_code,
        "device_name": device.device_name,
        "device_type": device.device_type,
        "station_id": device.station_id,
        "brand": device.brand,
        "model": device.model,
        "serial_number": device.serial_number,
        "rated_power": device.rated_power,
        "status": device.status,
        "latest_data": {
            "timestamp": latest.timestamp.isoformat() if latest else None,
            "power_kw": latest.power_kw if latest else None,
            "voltage_v": latest.voltage_v if latest else None,
            "current_a": latest.current_a if latest else None,
            "temperature": latest.temperature if latest else None,
            "daily_generation": latest.daily_generation if latest else None,
        },
    }


@router.get("/{device_id}/history")
async def get_device_history(
    device_id: int,
    start: datetime | None = None,
    end: datetime | None = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    """设备历史数据"""
    query = select(DeviceData).where(DeviceData.device_id == device_id)
    if start:
        query = query.where(DeviceData.timestamp >= start)
    if end:
        query = query.where(DeviceData.timestamp <= end)
    query = query.order_by(DeviceData.timestamp.desc()).limit(288)  # 一天5分钟粒度

    result = await db.execute(query)
    return [
        {
            "timestamp": row.timestamp.isoformat(),
            "power_kw": row.power_kw,
            "voltage_v": row.voltage_v,
            "current_a": row.current_a,
            "temperature": row.temperature,
            "daily_generation": row.daily_generation,
        }
        for row in result.scalars().all()
    ]
