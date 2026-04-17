"""电站管理接口"""
import logging
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.dependencies import get_current_user
from app.models.station import Station
from app.models.station_data import StationRealtime, StationDaily
from app.models.manufacturer import Manufacturer

logger = logging.getLogger(__name__)
router = APIRouter()


class StationCreate(BaseModel):
    name: str
    station_code: str
    manufacturer_id: int
    capacity_kwp: float | None = None
    address: str | None = None
    province: str | None = None
    city: str | None = None
    longitude: float | None = None
    latitude: float | None = None
    station_type: str | None = None
    grid_type: str | None = None
    electricity_price: float | None = None
    contact_name: str | None = None
    contact_phone: str | None = None


class StationUpdate(BaseModel):
    name: str | None = None
    capacity_kwp: float | None = None
    address: str | None = None
    electricity_price: float | None = None
    contact_name: str | None = None
    contact_phone: str | None = None
    is_active: bool | None = None


@router.get("")
async def list_stations(
    manufacturer_id: int | None = None,
    status: str | None = None,
    keyword: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    """电站列表 — 支持筛选和分页"""
    # 注意：自动同步已移到应用启动时执行，不在此处触发（避免请求阻塞和 session 冲突）

    query = (
        select(Station, StationRealtime, Manufacturer.name.label("manufacturer_name"))
        .outerjoin(StationRealtime, Station.id == StationRealtime.station_id)
        .join(Manufacturer, Station.manufacturer_id == Manufacturer.id)
    )

    if manufacturer_id:
        query = query.where(Station.manufacturer_id == manufacturer_id)
    if status:
        query = query.where(Station.status == status)
    if keyword:
        query = query.where(Station.name.ilike(f"%{keyword}%"))

    # 总数
    count_query = select(func.count(Station.id))
    if manufacturer_id:
        count_query = count_query.where(Station.manufacturer_id == manufacturer_id)
    if status:
        count_query = count_query.where(Station.status == status)
    if keyword:
        count_query = count_query.where(Station.name.ilike(f"%{keyword}%"))
    total = await db.scalar(count_query)

    # 分页
    result = await db.execute(
        query.offset((page - 1) * page_size).limit(page_size)
    )

    items = []
    for station, realtime, mfr_name in result.all():
        items.append({
            "id": station.id,
            "name": station.name,
            "station_code": station.station_code,
            "manufacturer_name": mfr_name,
            "manufacturer_id": station.manufacturer_id,
            "capacity_kwp": station.capacity_kwp,
            "address": station.address,
            "status": station.status,
            "longitude": station.longitude,
            "latitude": station.latitude,
            "current_power_kw": realtime.current_power_kw if realtime else None,
            "today_generation": realtime.today_generation if realtime else None,
            "total_generation": realtime.total_generation if realtime else None,
            "last_sync_at": station.last_sync_at.isoformat() if station.last_sync_at else None,
        })

    return {"total": total, "items": items, "page": page, "page_size": page_size}


@router.get("/{station_id}")
async def get_station(station_id: int, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    """电站详情"""
    result = await db.execute(
        select(Station).options(selectinload(Station.devices)).where(Station.id == station_id)
    )
    station = result.scalar_one_or_none()
    if not station:
        raise HTTPException(status_code=404, detail="电站不存在")

    # 实时数据
    rt = await db.scalar(select(StationRealtime).where(StationRealtime.station_id == station_id))

    return {
        "id": station.id,
        "name": station.name,
        "station_code": station.station_code,
        "manufacturer_id": station.manufacturer_id,
        "capacity_kwp": station.capacity_kwp,
        "address": station.address,
        "province": station.province,
        "city": station.city,
        "longitude": station.longitude,
        "latitude": station.latitude,
        "station_type": station.station_type,
        "grid_type": station.grid_type,
        "electricity_price": station.electricity_price,
        "contact_name": station.contact_name,
        "contact_phone": station.contact_phone,
        "status": station.status,
        "commissioned_date": station.commissioned_date.isoformat() if station.commissioned_date else None,
        "device_count": len(station.devices),
        "realtime": {
            "current_power_kw": rt.current_power_kw if rt else None,
            "today_generation": rt.today_generation if rt else None,
            "month_generation": rt.month_generation if rt else None,
            "year_generation": rt.year_generation if rt else None,
            "total_generation": rt.total_generation if rt else None,
            "today_revenue": rt.today_revenue if rt else None,
        },
    }


@router.post("")
async def create_station(data: StationCreate, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    station = Station(**data.model_dump())
    db.add(station)
    await db.commit()
    await db.refresh(station)
    return {"id": station.id, "name": station.name}


@router.put("/{station_id}")
async def update_station(station_id: int, data: StationUpdate, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    station = await db.get(Station, station_id)
    if not station:
        raise HTTPException(status_code=404, detail="电站不存在")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(station, k, v)
    await db.commit()
    return {"ok": True}


@router.get("/{station_id}/daily")
async def get_station_daily(
    station_id: int,
    start: date | None = None,
    end: date | None = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    """电站日发电数据"""
    query = select(StationDaily).where(StationDaily.station_id == station_id)
    if start:
        query = query.where(StationDaily.date >= start)
    if end:
        query = query.where(StationDaily.date <= end)
    query = query.order_by(StationDaily.date.desc()).limit(365)

    result = await db.execute(query)
    return [
        {
            "date": row.date.isoformat(),
            "generation_kwh": row.generation_kwh,
            "peak_power_kw": row.peak_power_kw,
            "revenue": row.revenue,
            "equivalent_hours": row.equivalent_hours,
            "pr_value": row.pr_value,
        }
        for row in result.scalars().all()
    ]
