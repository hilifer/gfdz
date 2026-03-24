"""同步日志模型"""
from datetime import datetime

from sqlalchemy import String, Text, DateTime, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class SyncLog(Base):
    __tablename__ = "sync_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    station_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("stations.id"))
    manufacturer_code: Mapped[str] = mapped_column(String(50), comment="厂家编码")
    sync_type: Mapped[str] = mapped_column(String(30), comment="类型: station_list/realtime/daily/alarm/device")
    status: Mapped[str] = mapped_column(String(20), comment="状态: success/partial/failed")
    records_count: Mapped[int] = mapped_column(Integer, default=0, comment="同步记录数")
    error_message: Mapped[str | None] = mapped_column(Text, comment="错误信息")
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime)
