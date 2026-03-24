"""设备模型"""
from datetime import datetime

from sqlalchemy import String, Boolean, DateTime, Float, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(primary_key=True)
    station_id: Mapped[int] = mapped_column(Integer, ForeignKey("stations.id"))
    device_code: Mapped[str] = mapped_column(String(100), comment="设备编码")
    device_name: Mapped[str] = mapped_column(String(200), comment="设备名称")
    device_type: Mapped[str] = mapped_column(String(30), comment="类型: inverter/meter/combiner_box/weather_station/storage")
    brand: Mapped[str | None] = mapped_column(String(100), comment="品牌")
    model: Mapped[str | None] = mapped_column(String(100), comment="型号")
    serial_number: Mapped[str | None] = mapped_column(String(100), comment="序列号")
    rated_power: Mapped[float | None] = mapped_column(Float, comment="额定功率(kW)")
    status: Mapped[str] = mapped_column(String(20), default="normal", comment="状态: normal/fault/offline")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_data_at: Mapped[datetime | None] = mapped_column(DateTime, comment="最后数据时间")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

    station = relationship("Station", back_populates="devices")
