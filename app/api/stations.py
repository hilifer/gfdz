"""电站管理API"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.power_station import PowerStation
from app.models.generation_data import GenerationData
from app.models.alarm import Alarm
from app.schemas.schemas import (
    StationCreate, StationUpdate, StationResponse,
    GenerationDataResponse, AlarmResponse,
)

router = APIRouter(prefix="/api/stations", tags=["电站管理"])


@router.get("", response_model=list[StationResponse])
async def list_stations(
    manufacturer_id: int | None = None,
    is_active: bool | None = None,
    db: AsyncSession = Depends(get_db),
):
    q = select(PowerStation)
    if manufacturer_id is not None:
        q = q.where(PowerStation.manufacturer_id == manufacturer_id)
    if is_active is not None:
        q = q.where(PowerStation.is_active == is_active)
    q = q.order_by(PowerStation.id)
    result = await db.execute(q)
    return result.scalars().all()


@router.get("/{sid}", response_model=StationResponse)
async def get_station(sid: int, db: AsyncSession = Depends(get_db)):
    s = await db.get(PowerStation, sid)
    if not s:
        raise HTTPException(404, "电站不存在")
    return s


@router.post("", response_model=StationResponse)
async def create_station(data: StationCreate, db: AsyncSession = Depends(get_db)):
    s = PowerStation(**data.model_dump())
    db.add(s)
    await db.commit()
    await db.refresh(s)
    return s


@router.put("/{sid}", response_model=StationResponse)
async def update_station(sid: int, data: StationUpdate, db: AsyncSession = Depends(get_db)):
    s = await db.get(PowerStation, sid)
    if not s:
        raise HTTPException(404, "电站不存在")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(s, k, v)
    await db.commit()
    await db.refresh(s)
    return s


@router.delete("/{sid}")
async def delete_station(sid: int, db: AsyncSession = Depends(get_db)):
    s = await db.get(PowerStation, sid)
    if not s:
        raise HTTPException(404, "电站不存在")
    await db.delete(s)
    await db.commit()
    return {"message": "已删除"}


@router.get("/{sid}/generation", response_model=list[GenerationDataResponse])
async def get_station_generation(
    sid: int,
    limit: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
):
    q = (
        select(GenerationData)
        .where(GenerationData.station_id == sid)
        .order_by(GenerationData.record_date.desc())
        .limit(limit)
    )
    result = await db.execute(q)
    return result.scalars().all()


@router.get("/{sid}/alarms", response_model=list[AlarmResponse])
async def get_station_alarms(
    sid: int,
    status: str | None = None,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(Alarm).where(Alarm.station_id == sid)
    if status:
        q = q.where(Alarm.status == status)
    q = q.order_by(Alarm.alarm_time.desc()).limit(limit)
    result = await db.execute(q)
    return result.scalars().all()
