"""设备时序数据"""
from datetime import datetime

from sqlalchemy import Float, DateTime, Integer, ForeignKey, Text, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class DeviceData(Base):
    """设备时序数据 — 5分钟粒度"""
    __tablename__ = "device_data"
    __table_args__ = (
        Index("idx_device_data_ts", "device_id", "timestamp"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    device_id: Mapped[int] = mapped_column(Integer, ForeignKey("devices.id"))
    timestamp: Mapped[datetime] = mapped_column(DateTime, comment="采集时间")

    # 逆变器通用字段
    power_kw: Mapped[float | None] = mapped_column(Float, comment="功率(kW)")
    voltage_v: Mapped[float | None] = mapped_column(Float, comment="电压(V)")
    current_a: Mapped[float | None] = mapped_column(Float, comment="电流(A)")
    temperature: Mapped[float | None] = mapped_column(Float, comment="温度(℃)")
    frequency: Mapped[float | None] = mapped_column(Float, comment="频率(Hz)")
    daily_generation: Mapped[float | None] = mapped_column(Float, comment="日发电量(kWh)")

    # 各厂家差异化字段存JSON
    raw_data: Mapped[str | None] = mapped_column(Text, comment="原始数据JSON")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
