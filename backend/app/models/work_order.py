"""工单模型"""
from datetime import datetime

from sqlalchemy import String, Text, DateTime, Integer, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class WorkOrder(Base):
    __tablename__ = "work_orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_no: Mapped[str] = mapped_column(String(50), unique=True, comment="工单编号")
    title: Mapped[str] = mapped_column(String(200), comment="工单标题")
    station_id: Mapped[int] = mapped_column(Integer, ForeignKey("stations.id"))
    device_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("devices.id"))
    alarm_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("alarms.id"))

    order_type: Mapped[str] = mapped_column(String(30), comment="类型: corrective/preventive/inspection/cleaning")
    priority: Mapped[str] = mapped_column(String(20), default="medium", comment="优先级: low/medium/high/urgent")
    status: Mapped[str] = mapped_column(String(20), default="pending", comment="状态: pending/assigned/in_progress/completed/closed")
    description: Mapped[str | None] = mapped_column(Text, comment="描述")
    resolution: Mapped[str | None] = mapped_column(Text, comment="处理结果")
    cost: Mapped[float | None] = mapped_column(Float, comment="费用")

    creator_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    assignee_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"))

    started_at: Mapped[datetime | None] = mapped_column(DateTime)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)


class WorkOrderLog(Base):
    __tablename__ = "work_order_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    work_order_id: Mapped[int] = mapped_column(Integer, ForeignKey("work_orders.id"))
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    action: Mapped[str] = mapped_column(String(30), comment="动作: created/assigned/started/commented/completed/closed")
    content: Mapped[str | None] = mapped_column(Text, comment="内容")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
