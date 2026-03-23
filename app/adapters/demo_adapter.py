"""
示例适配器 - 用于演示和测试。

当你拿到新的厂家API协议文档后，参考此文件创建对应的适配器：
1. 继承 BaseAdapter
2. 用 @AdapterRegistry.register("厂家编码") 注册
3. 实现所有抽象方法
"""
import random
from datetime import date, datetime

from app.adapters.base import BaseAdapter, StationInfo, GenerationRecord, AlarmRecord
from app.adapters.registry import AdapterRegistry


@AdapterRegistry.register("demo")
class DemoAdapter(BaseAdapter):
    """演示适配器，生成模拟数据用于测试"""

    async def authenticate(self) -> bool:
        self._token = "demo-token"
        return True

    async def get_station_list(self) -> list[StationInfo]:
        return [
            StationInfo(
                station_code="DEMO-001",
                name="演示电站1号",
                capacity=100.0,
                status="normal",
            ),
            StationInfo(
                station_code="DEMO-002",
                name="演示电站2号",
                capacity=200.0,
                status="normal",
            ),
        ]

    async def get_station_realtime(self, station_code: str) -> GenerationRecord | None:
        power = round(random.uniform(10, 80), 2)
        return GenerationRecord(
            record_date=date.today(),
            current_power=power,
            daily_generation=round(power * random.uniform(3, 6), 2),
            total_generation=round(random.uniform(50000, 200000), 2),
        )

    async def get_station_daily(self, station_code: str, query_date: date) -> GenerationRecord | None:
        daily = round(random.uniform(100, 500), 2)
        return GenerationRecord(
            record_date=query_date,
            daily_generation=daily,
            monthly_generation=round(daily * 15, 2),
            yearly_generation=round(daily * 180, 2),
            total_generation=round(random.uniform(50000, 200000), 2),
            daily_peak_power=round(random.uniform(50, 150), 2),
            equivalent_hours=round(random.uniform(3, 6), 2),
            pr_value=round(random.uniform(0.75, 0.90), 4),
            daily_income=round(daily * 0.45, 2),
        )

    async def get_station_alarms(self, station_code: str) -> list[AlarmRecord]:
        if random.random() > 0.5:
            return []
        return [
            AlarmRecord(
                alarm_name="通讯中断告警",
                alarm_time=datetime.now(),
                alarm_code="COMM_001",
                alarm_level="warning",
                description="设备通讯中断超过5分钟",
                device_name="逆变器-01",
            ),
        ]
