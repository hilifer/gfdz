"""告警中心接口"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.alarm import Alarm
from app.models.station import Station
from app.models.user import User

router = APIRouter()


@router.get("")
async def list_alarms(
    station_id: int | None = None,
    alarm_level: str | None = None,
    status: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    """告警列表"""
    query = select(Alarm, Station.name.label("station_name")).join(Station)

    if station_id:
        query = query.where(Alarm.station_id == station_id)
    if alarm_level:
        query = query.where(Alarm.alarm_level == alarm_level)
    if status:
        query = query.where(Alarm.status == status)

    count_q = select(func.count(Alarm.id))
    if station_id:
        count_q = count_q.where(Alarm.station_id == station_id)
    if status:
        count_q = count_q.where(Alarm.status == status)
    total = await db.scalar(count_q)

    result = await db.execute(
        query.order_by(Alarm.alarm_time.desc()).offset((page - 1) * page_size).limit(page_size)
    )

    items = []
    for alarm, station_name in result.all():
        items.append({
            "id": alarm.id,
            "station_name": station_name,
            "station_id": alarm.station_id,
            "alarm_code": alarm.alarm_code,
            "alarm_name": alarm.alarm_name,
            "alarm_level": alarm.alarm_level,
            "alarm_time": alarm.alarm_time.isoformat(),
            "recover_time": alarm.recover_time.isoformat() if alarm.recover_time else None,
            "status": alarm.status,
            "device_name": alarm.device_name,
        })

    return {"total": total, "items": items, "page": page, "page_size": page_size}


@router.get("/stats")
async def alarm_stats(db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    """告警统计"""
    result = await db.execute(
        select(Alarm.alarm_level, func.count(Alarm.id))
        .where(Alarm.status == "active")
        .group_by(Alarm.alarm_level)
    )
    stats = {row[0]: row[1] for row in result.all()}
    return {
        "critical": stats.get("critical", 0),
        "warning": stats.get("warning", 0),
        "info": stats.get("info", 0),
        "total_active": sum(stats.values()),
    }


@router.post("/{alarm_id}/confirm")
async def confirm_alarm(alarm_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    """确认告警"""
    alarm = await db.get(Alarm, alarm_id)
    if not alarm:
        raise HTTPException(status_code=404, detail="告警不存在")
    alarm.status = "confirmed"
    alarm.confirmed_by = user.id
    alarm.confirmed_at = datetime.now()
    await db.commit()
    return {"ok": True}
