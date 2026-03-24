"""工单管理接口"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.work_order import WorkOrder, WorkOrderLog
from app.models.user import User

router = APIRouter()


class WorkOrderCreate(BaseModel):
    title: str
    station_id: int
    device_id: int | None = None
    alarm_id: int | None = None
    order_type: str = "corrective"
    priority: str = "medium"
    description: str | None = None


@router.get("")
async def list_work_orders(
    status: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    query = select(WorkOrder)
    if status:
        query = query.where(WorkOrder.status == status)

    total = await db.scalar(select(func.count(WorkOrder.id)))
    result = await db.execute(
        query.order_by(WorkOrder.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    )

    items = []
    for wo in result.scalars().all():
        items.append({
            "id": wo.id,
            "order_no": wo.order_no,
            "title": wo.title,
            "station_id": wo.station_id,
            "order_type": wo.order_type,
            "priority": wo.priority,
            "status": wo.status,
            "created_at": wo.created_at.isoformat(),
        })

    return {"total": total, "items": items, "page": page, "page_size": page_size}


@router.post("")
async def create_work_order(data: WorkOrderCreate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    # 生成工单号
    count = await db.scalar(select(func.count(WorkOrder.id))) or 0
    order_no = f"WO{datetime.now().strftime('%Y%m%d')}{count + 1:04d}"

    wo = WorkOrder(
        order_no=order_no,
        title=data.title,
        station_id=data.station_id,
        device_id=data.device_id,
        alarm_id=data.alarm_id,
        order_type=data.order_type,
        priority=data.priority,
        description=data.description,
        creator_id=user.id,
    )
    db.add(wo)
    await db.flush()

    # 创建日志
    log = WorkOrderLog(work_order_id=wo.id, user_id=user.id, action="created", content="创建工单")
    db.add(log)
    await db.commit()
    return {"id": wo.id, "order_no": order_no}


@router.post("/{wo_id}/complete")
async def complete_work_order(wo_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    wo = await db.get(WorkOrder, wo_id)
    if not wo:
        raise HTTPException(status_code=404, detail="工单不存在")
    wo.status = "completed"
    wo.completed_at = datetime.now()
    log = WorkOrderLog(work_order_id=wo.id, user_id=user.id, action="completed", content="完成工单")
    db.add(log)
    await db.commit()
    return {"ok": True}
