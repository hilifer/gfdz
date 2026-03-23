"""厂家模型"""
from datetime import datetime
from sqlalchemy import String, Text, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Manufacturer(Base):
    __tablename__ = "manufacturers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, comment="厂家名称")
    code: Mapped[str] = mapped_column(String(50), unique=True, comment="厂家编码，用于匹配适配器")
    api_base_url: Mapped[str | None] = mapped_column(String(500), comment="API基础地址")
    adapter_class: Mapped[str] = mapped_column(String(100), comment="适配器类名")
    auth_config: Mapped[str | None] = mapped_column(Text, comment="认证配置JSON")
    description: Mapped[str | None] = mapped_column(Text, comment="厂家描述")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否启用")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

    stations = relationship("PowerStation", back_populates="manufacturer")
