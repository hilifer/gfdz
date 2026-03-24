"""电站模型"""
from datetime import datetime, date

from sqlalchemy import String, Text, Boolean, DateTime, Float, Integer, ForeignKey, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Station(Base):
    __tablename__ = "stations"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), comment="电站名称")
    station_code: Mapped[str] = mapped_column(String(100), comment="厂家平台编码")
    manufacturer_id: Mapped[int] = mapped_column(Integer, ForeignKey("manufacturers.id"))

    # 基本信息
    capacity_kwp: Mapped[float | None] = mapped_column(Float, comment="装机容量(kWp)")
    address: Mapped[str | None] = mapped_column(String(500), comment="地址")
    province: Mapped[str | None] = mapped_column(String(50), comment="省份")
    city: Mapped[str | None] = mapped_column(String(50), comment="城市")
    longitude: Mapped[float | None] = mapped_column(Float, comment="经度")
    latitude: Mapped[float | None] = mapped_column(Float, comment="纬度")

    # 业务信息
    station_type: Mapped[str | None] = mapped_column(String(30), comment="类型: rooftop/ground/distributed")
    grid_type: Mapped[str | None] = mapped_column(String(30), comment="并网类型: full_feed/self_use")
    commissioned_date: Mapped[date | None] = mapped_column(Date, comment="并网日期")
    electricity_price: Mapped[float | None] = mapped_column(Float, comment="电价(元/kWh)")
    feed_in_price: Mapped[float | None] = mapped_column(Float, comment="上网电价(元/kWh)")

    # 联系人
    contact_name: Mapped[str | None] = mapped_column(String(50), comment="联系人")
    contact_phone: Mapped[str | None] = mapped_column(String(20), comment="联系电话")

    # 状态
    status: Mapped[str] = mapped_column(String(20), default="normal", comment="状态: normal/fault/offline")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_sync_at: Mapped[datetime | None] = mapped_column(DateTime)
    extra_config: Mapped[str | None] = mapped_column(Text, comment="额外配置JSON")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 关系
    manufacturer = relationship("Manufacturer", back_populates="stations")
    devices = relationship("Device", back_populates="station")
    alarms = relationship("Alarm", back_populates="station")
