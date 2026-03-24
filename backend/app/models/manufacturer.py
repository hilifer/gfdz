"""厂家模型"""
from datetime import datetime

from sqlalchemy import String, Text, Boolean, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Manufacturer(Base):
    __tablename__ = "manufacturers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, comment="厂家名称")
    code: Mapped[str] = mapped_column(String(50), unique=True, comment="厂家编码: huawei/sungrow/aiswei")
    api_base_url: Mapped[str | None] = mapped_column(String(500), comment="API基础地址")
    auth_config: Mapped[str | None] = mapped_column(Text, comment="认证配置JSON")
    sync_interval: Mapped[int] = mapped_column(Integer, default=300, comment="同步间隔(秒)")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_sync_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

    stations = relationship("Station", back_populates="manufacturer")
