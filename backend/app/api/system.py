"""系统设置接口"""
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, require_role, hash_password
from app.models.user import User
from app.models.sync_log import SyncLog

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
