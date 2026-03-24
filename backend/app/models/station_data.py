"""电站数据模型"""
from datetime import datetime, date

from sqlalchemy import Float, DateTime, Date, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class StationRealtime(Base):
    """电站实时快照 — 每次同步覆盖"""
    __tablename__ = "station_realtime"

    id: Mapped[int] = mapped_column(primary_key=True)
    station_id: Mapped[int] = mapped_column(Integer, ForeignKey("stations.id"), unique=True)
    current_power_kw: Mapped[float | None] = mapped_column(Float, comment="实时功率(kW)")
    today_generation: Mapped[float | None] = mapped_column(Float, comment="今日发电量(kWh)")
    month_generation: Mapped[float | None] = mapped_column(Float, comment="本月发电量(kWh)")
    year_generation: Mapped[float | None] = mapped_column(Float, comment="本年发电量(kWh)")
    total_generation: Mapped[float | None] = mapped_column(Float, comment="累计发电量(kWh)")
    today_revenue: Mapped[float | None] = mapped_column(Float, comment="今日收益(元)")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)


class StationDaily(Base):
    """电站日统计数据"""
    __tablename__ = "station_daily"
    __table_args__ = (
        UniqueConstraint("station_id", "date", name="uq_station_daily"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    station_id: Mapped[int] = mapped_column(Integer, ForeignKey("stations.id"))
    date: Mapped[date] = mapped_column(Date, comment="日期")
    generation_kwh: Mapped[float | None] = mapped_column(Float, comment="日发电量(kWh)")
    peak_power_kw: Mapped[float | None] = mapped_column(Float, comment="峰值功率(kW)")
    revenue: Mapped[float | None] = mapped_column(Float, comment="日收益(元)")
    equivalent_hours: Mapped[float | None] = mapped_column(Float, comment="等效小时数")
    pr_value: Mapped[float | None] = mapped_column(Float, comment="PR性能比")
    co2_reduction: Mapped[float | None] = mapped_column(Float, comment="CO2减排(kg)")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
