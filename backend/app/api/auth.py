"""认证接口"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.dependencies import verify_password, create_token, get_current_user

router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str
    user: dict


class UserInfo(BaseModel):
    id: int
    username: str
    display_name: str
    role: str
    phone: str | None = None
    email: str | None = None


@router.post("/login", response_model=LoginResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == req.username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="账号已禁用")

    user.last_login_at = datetime.now()
    await db.commit()

    token = create_token(user.id, user.username)
    return LoginResponse(
        token=token,
        user={
            "id": user.id,
            "username": user.username,
            "display_name": user.display_name,
            "role": user.role,
        },
    )


@router.get("/me", response_model=UserInfo)
async def get_me(user: User = Depends(get_current_user)):
    return UserInfo(
        id=user.id,
        username=user.username,
        display_name=user.display_name,
        role=user.role,
        phone=user.phone,
        email=user.email,
    )
