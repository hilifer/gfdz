"""仪表盘API"""
from datetime import date, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.manufacturer import Manufacturer
from app.models.power_station import PowerStation
from app.models.generation_data import GenerationData
from app.models.alarm import Alarm

router = APIRouter(prefix="/api/dashboard", tags=["仪表盘"])


@router.get("/summary")
async def get_summary(db: AsyncSession = Depends(get_db)):
    """获取总览数据"""
    # 电站总数
    station_count = (await db.execute(
        select(func.count(PowerStation.id))
    )).scalar() or 0

    # 活跃电站数
    active_count = (await db.execute(
        select(func.count(PowerStation.id)).where(PowerStation.is_active == True)
    )).scalar() or 0

    # 厂家数
    manufacturer_count = (await db.execute(
        select(func.count(Manufacturer.id))
    )).scalar() or 0

    # 总装机容量
    total_capacity = (await db.execute(
        select(func.sum(PowerStation.capacity)).where(PowerStation.is_active == True)
    )).scalar() or 0

    # 今日发电量
    today = date.today()
    today_generation = (await db.execute(
        select(func.sum(GenerationData.daily_generation))
        .where(GenerationData.record_date == today)
    )).scalar() or 0

    # 活跃告警数
    active_alarms = (await db.execute(
        select(func.count(Alarm.id)).where(Alarm.status == "active")
    )).scalar() or 0

    # 故障电站数
    fault_count = (await db.execute(
        select(func.count(PowerStation.id)).where(PowerStation.status == "fault")
    )).scalar() or 0

    return {
        "station_count": station_count,
        "active_count": active_count,
        "manufacturer_count": manufacturer_count,
        "total_capacity": round(total_capacity, 2),
        "today_generation": round(today_generation, 2),
        "active_alarms": active_alarms,
        "fault_count": fault_count,
    }


@router.get("/generation_trend")
async def get_generation_trend(days: int = 7, db: AsyncSession = Depends(get_db)):
    """获取近N天发电量趋势"""
    start_date = date.today() - timedelta(days=days - 1)
    result = await db.execute(
        select(
            GenerationData.record_date,
            func.sum(GenerationData.daily_generation).label("total"),
        )
        .where(GenerationData.record_date >= start_date)
        .group_by(GenerationData.record_date)
        .order_by(GenerationData.record_date)
    )
    rows = result.all()
    return [{"date": str(r.record_date), "generation": round(r.total or 0, 2)} for r in rows]


@router.get("/station_status")
async def get_station_status(db: AsyncSession = Depends(get_db)):
    """获取各电站当前状态"""
    result = await db.execute(
        select(PowerStation).where(PowerStation.is_active == True).order_by(PowerStation.id)
    )
    stations = result.scalars().all()
    items = []
    for s in stations:
        # 获取最新发电数据
        gen_result = await db.execute(
            select(GenerationData)
            .where(GenerationData.station_id == s.id)
            .order_by(GenerationData.record_date.desc())
            .limit(1)
        )
        latest = gen_result.scalar_one_or_none()
        items.append({
            "id": s.id,
            "name": s.name,
            "station_code": s.station_code,
            "capacity": s.capacity,
            "status": s.status,
            "current_power": latest.current_power if latest else None,
            "daily_generation": latest.daily_generation if latest else None,
            "last_sync_at": str(s.last_sync_at) if s.last_sync_at else None,
        })
    return items
