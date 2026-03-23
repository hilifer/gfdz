"""电站模型"""
from datetime import datetime
from sqlalchemy import String, Text, DateTime, Boolean, Float, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class PowerStation(Base):
    __tablename__ = "power_stations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), comment="电站名称")
    station_code: Mapped[str] = mapped_column(String(100), comment="电站在厂家平台的编码")
    manufacturer_id: Mapped[int] = mapped_column(Integer, ForeignKey("manufacturers.id"), comment="所属厂家")
    capacity: Mapped[float | None] = mapped_column(Float, comment="装机容量(kWp)")
    location: Mapped[str | None] = mapped_column(String(500), comment="电站地址")
    longitude: Mapped[float | None] = mapped_column(Float, comment="经度")
    latitude: Mapped[float | None] = mapped_column(Float, comment="纬度")
    contact_person: Mapped[str | None] = mapped_column(String(50), comment="联系人")
    contact_phone: Mapped[str | None] = mapped_column(String(20), comment="联系电话")
    extra_params: Mapped[str | None] = mapped_column(Text, comment="额外参数JSON，不同厂家的特殊配置")
    status: Mapped[str] = mapped_column(String(20), default="normal", comment="状态: normal/fault/offline")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否启用监控")
    last_sync_at: Mapped[datetime | None] = mapped_column(DateTime, comment="最后同步时间")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

    manufacturer = relationship("Manufacturer", back_populates="stations")
    generation_data = relationship("GenerationData", back_populates="station", order_by="desc(GenerationData.record_date)")
    alarms = relationship("Alarm", back_populates="station", order_by="desc(Alarm.alarm_time)")
