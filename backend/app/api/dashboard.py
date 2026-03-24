"""总览大屏接口"""
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.station import Station
from app.models.station_data import StationRealtime
from app.models.alarm import Alarm

router = APIRouter()


@router.get("/summary")
async def get_summary(db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    """总览数据：总电站数、总装机、总发电、告警数"""
    # 电站统计
    station_count = await db.scalar(select(func.count(Station.id)).where(Station.is_active == True))
    total_capacity = await db.scalar(select(func.sum(Station.capacity_kwp)).where(Station.is_active == True)) or 0

    # 实时发电汇总
    today_gen = await db.scalar(select(func.sum(StationRealtime.today_generation))) or 0
    current_power = await db.scalar(select(func.sum(StationRealtime.current_power_kw))) or 0
    total_gen = await db.scalar(select(func.sum(StationRealtime.total_generation))) or 0

    # 告警统计
    active_alarms = await db.scalar(
        select(func.count(Alarm.id)).where(Alarm.status == "active")
    )

    # 电站状态分布
    status_result = await db.execute(
        select(Station.status, func.count(Station.id))
        .where(Station.is_active == True)
        .group_by(Station.status)
    )
    status_dist = {row[0]: row[1] for row in status_result.all()}

    return {
        "station_count": station_count,
        "total_capacity_kwp": round(total_capacity, 2),
        "current_power_kw": round(current_power, 2),
        "today_generation_kwh": round(today_gen, 2),
        "total_generation_kwh": round(total_gen, 2),
        "active_alarms": active_alarms,
        "status_distribution": status_dist,
    }


@router.get("/map")
async def get_map_data(db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    """地图数据：所有电站位置 + 状态"""
    result = await db.execute(
        select(
            Station.id, Station.name, Station.longitude, Station.latitude,
            Station.status, Station.capacity_kwp,
            StationRealtime.current_power_kw, StationRealtime.today_generation,
        )
        .outerjoin(StationRealtime, Station.id == StationRealtime.station_id)
        .where(Station.is_active == True)
    )

    stations = []
    for row in result.all():
        if row.longitude and row.latitude:
            stations.append({
                "id": row.id,
                "name": row.name,
                "lng": row.longitude,
                "lat": row.latitude,
                "status": row.status,
                "capacity_kwp": row.capacity_kwp,
                "current_power_kw": row.current_power_kw,
                "today_generation": row.today_generation,
            })
    return stations
