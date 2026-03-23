"""发电数据模型"""
from datetime import datetime, date
from sqlalchemy import Integer, Float, DateTime, Date, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class GenerationData(Base):
    __tablename__ = "generation_data"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    station_id: Mapped[int] = mapped_column(Integer, ForeignKey("power_stations.id"), comment="电站ID")
    record_date: Mapped[date] = mapped_column(Date, comment="记录日期")
    daily_generation: Mapped[float | None] = mapped_column(Float, comment="日发电量(kWh)")
    monthly_generation: Mapped[float | None] = mapped_column(Float, comment="月累计发电量(kWh)")
    yearly_generation: Mapped[float | None] = mapped_column(Float, comment="年累计发电量(kWh)")
    total_generation: Mapped[float | None] = mapped_column(Float, comment="总发电量(kWh)")
    current_power: Mapped[float | None] = mapped_column(Float, comment="当前功率(kW)")
    daily_income: Mapped[float | None] = mapped_column(Float, comment="日收益(元)")
    daily_peak_power: Mapped[float | None] = mapped_column(Float, comment="日峰值功率(kW)")
    equivalent_hours: Mapped[float | None] = mapped_column(Float, comment="等效利用小时数")
    pr_value: Mapped[float | None] = mapped_column(Float, comment="PR值(性能比)")
    raw_data: Mapped[str | None] = mapped_column(Text, comment="原始数据JSON")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    station = relationship("PowerStation", back_populates="generation_data")
