"""厂家管理API"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.manufacturer import Manufacturer
from app.schemas.schemas import ManufacturerCreate, ManufacturerUpdate, ManufacturerResponse

router = APIRouter(prefix="/api/manufacturers", tags=["厂家管理"])


@router.get("", response_model=list[ManufacturerResponse])
async def list_manufacturers(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Manufacturer).order_by(Manufacturer.id))
    return result.scalars().all()


@router.get("/{mid}", response_model=ManufacturerResponse)
async def get_manufacturer(mid: int, db: AsyncSession = Depends(get_db)):
    m = await db.get(Manufacturer, mid)
    if not m:
        raise HTTPException(404, "厂家不存在")
    return m


@router.post("", response_model=ManufacturerResponse)
async def create_manufacturer(data: ManufacturerCreate, db: AsyncSession = Depends(get_db)):
    m = Manufacturer(**data.model_dump())
    db.add(m)
    await db.commit()
    await db.refresh(m)
    return m


@router.put("/{mid}", response_model=ManufacturerResponse)
async def update_manufacturer(mid: int, data: ManufacturerUpdate, db: AsyncSession = Depends(get_db)):
    m = await db.get(Manufacturer, mid)
    if not m:
        raise HTTPException(404, "厂家不存在")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(m, k, v)
    await db.commit()
    await db.refresh(m)
    return m


@router.delete("/{mid}")
async def delete_manufacturer(mid: int, db: AsyncSession = Depends(get_db)):
    m = await db.get(Manufacturer, mid)
    if not m:
        raise HTTPException(404, "厂家不存在")
    await db.delete(m)
    await db.commit()
    return {"message": "已删除"}
