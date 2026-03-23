"""告警模型"""
from datetime import datetime
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Alarm(Base):
    __tablename__ = "alarms"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    station_id: Mapped[int] = mapped_column(Integer, ForeignKey("power_stations.id"), comment="电站ID")
    alarm_code: Mapped[str | None] = mapped_column(String(50), comment="告警编码")
    alarm_name: Mapped[str] = mapped_column(String(200), comment="告警名称")
    alarm_level: Mapped[str] = mapped_column(String(20), default="info", comment="告警级别: info/warning/critical")
    alarm_time: Mapped[datetime] = mapped_column(DateTime, comment="告警时间")
    recover_time: Mapped[datetime | None] = mapped_column(DateTime, comment="恢复时间")
    status: Mapped[str] = mapped_column(String(20), default="active", comment="状态: active/recovered")
    description: Mapped[str | None] = mapped_column(Text, comment="告警描述")
    device_name: Mapped[str | None] = mapped_column(String(100), comment="设备名称")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    station = relationship("PowerStation", back_populates="alarms")
