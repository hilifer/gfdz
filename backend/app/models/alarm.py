"""告警模型"""
from datetime import datetime

from sqlalchemy import String, Text, Boolean, DateTime, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Alarm(Base):
    __tablename__ = "alarms"

    id: Mapped[int] = mapped_column(primary_key=True)
    station_id: Mapped[int] = mapped_column(Integer, ForeignKey("stations.id"))
    device_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("devices.id"))

    alarm_code: Mapped[str | None] = mapped_column(String(50), comment="告警编码")
    alarm_name: Mapped[str] = mapped_column(String(200), comment="告警名称")
    alarm_level: Mapped[str] = mapped_column(String(20), default="info", comment="级别: info/warning/critical")
    alarm_time: Mapped[datetime] = mapped_column(DateTime, comment="告警时间")
    recover_time: Mapped[datetime | None] = mapped_column(DateTime, comment="恢复时间")
    status: Mapped[str] = mapped_column(String(20), default="active", comment="状态: active/confirmed/recovered")
    description: Mapped[str | None] = mapped_column(Text, comment="描述")
    device_name: Mapped[str | None] = mapped_column(String(100), comment="设备名称")

    # 确认
    confirmed_by: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"))
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    station = relationship("Station", back_populates="alarms")
