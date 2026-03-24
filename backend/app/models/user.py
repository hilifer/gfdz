"""用户模型"""
from datetime import datetime

from sqlalchemy import String, Boolean, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, comment="用户名")
    password_hash: Mapped[str] = mapped_column(String(200), comment="密码哈希")
    display_name: Mapped[str] = mapped_column(String(100), comment="显示名称")
    phone: Mapped[str | None] = mapped_column(String(20), comment="手机号")
    email: Mapped[str | None] = mapped_column(String(100), comment="邮箱")
    role: Mapped[str] = mapped_column(String(20), default="viewer", comment="角色: admin/operator/viewer")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)
