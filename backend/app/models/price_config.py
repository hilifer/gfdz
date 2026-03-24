"""电价配置模型"""
from datetime import datetime, date

from sqlalchemy import String, Text, Boolean, DateTime, Float, Integer, ForeignKey, Date
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class PriceConfig(Base):
    __tablename__ = "price_configs"

    id: Mapped[int] = mapped_column(primary_key=True)
    station_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("stations.id"), comment="电站ID，空表示全局默认")
    policy_name: Mapped[str] = mapped_column(String(100), comment="策略名称")
    policy_type: Mapped[str] = mapped_column(String(20), comment="类型: fixed/tou(分时)")

    # 固定电价
    fixed_price: Mapped[float | None] = mapped_column(Float, comment="固定电价(元/kWh)")

    # 分时电价
    peak_price: Mapped[float | None] = mapped_column(Float, comment="尖峰电价")
    flat_price: Mapped[float | None] = mapped_column(Float, comment="平段电价")
    valley_price: Mapped[float | None] = mapped_column(Float, comment="谷段电价")
    peak_hours: Mapped[str | None] = mapped_column(Text, comment="尖峰时段JSON")
    valley_hours: Mapped[str | None] = mapped_column(Text, comment="谷段时段JSON")

    # 补贴
    feed_in_tariff: Mapped[float | None] = mapped_column(Float, comment="上网电价")
    government_subsidy: Mapped[float | None] = mapped_column(Float, comment="补贴(元/kWh)")

    effective_from: Mapped[date | None] = mapped_column(Date, comment="生效日期")
    effective_to: Mapped[date | None] = mapped_column(Date, comment="失效日期")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
