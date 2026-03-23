"""智能限流管理器

支持两种限流粒度：
1. 接口级限流 - 华为每个接口有独立的限流规则（基于电站/设备数量动态计算）
2. 平台级限流 - 爱士惟全局100次/分钟

华为限流规则参考 SmartPVMS_V600R024C10_北向接口参考-V6.pdf：
- 登录/登出: 每10分钟5次
- 电站列表: 每天 ceil(站数/100)*10+24 次
- 电站实时: 每5分钟 ceil(站数/100) 次，并发1分钟1次
- 电站日/月/年: 每天 ceil(站数/100)+24 次，并发1分钟1次
- 设备列表: 每天 ceil(站数/100)+24 次
- 设备实时: 每5分钟 Σceil(各类设备数/100) 次
- 设备历史5min: 每天 Σceil(各类设备数/10)+24 次，并发1分钟1次
- 设备历史日/月/年: 每天 Σceil(各类设备数/100)+24 次，并发1分钟1次
- 告警: 每30分钟 MAX(ceil(站数/100), Σceil(各类设备数/100)) 次
- 告警(历史): 每1小时1次

爱士惟限流规则：
- 全局: OLDAPI 100次/分钟
"""
import asyncio
import logging
import math
import time
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class EndpointLimit:
    """单个接口的限流配置"""
    max_calls: int            # 最大调用次数
    period_seconds: float     # 时间窗口（秒）
    min_interval: float = 0   # 最小调用间隔（秒），0表示无限制


class EndpointLimiter:
    """单接口限流器 - 滑动窗口 + 最小间隔"""

    def __init__(self, limit: EndpointLimit):
        self.limit = limit
        self._call_times: list[float] = []
        self._last_call: float = 0
        self._lock = asyncio.Lock()
        # 统计
        self.total_calls = 0
        self.total_waits = 0
        self.total_throttled = 0

    async def acquire(self) -> float:
        """
        获取调用许可。
        返回实际等待的时间（秒）。如果无法获取（配额已耗尽），抛出异常。
        """
        total_wait = 0.0
        async with self._lock:
            now = time.monotonic()

            # 清理过期记录
            cutoff = now - self.limit.period_seconds
            self._call_times = [t for t in self._call_times if t > cutoff]

            # 检查窗口内调用次数
            if len(self._call_times) >= self.limit.max_calls:
                # 需要等待最早的调用过期
                earliest = self._call_times[0]
                wait_time = (earliest + self.limit.period_seconds) - now + 0.1
                if wait_time > 0:
                    self.total_waits += 1
                    total_wait += wait_time
                    logger.info(f"接口限流等待 {wait_time:.1f}s (窗口内已调用{len(self._call_times)}次)")
                    # 释放锁再等待
                    self._lock.release()
                    await asyncio.sleep(wait_time)
                    await self._lock.acquire()
                    now = time.monotonic()
                    cutoff = now - self.limit.period_seconds
                    self._call_times = [t for t in self._call_times if t > cutoff]

            # 检查最小间隔
            if self.limit.min_interval > 0 and self._last_call > 0:
                elapsed = now - self._last_call
                if elapsed < self.limit.min_interval:
                    wait_time = self.limit.min_interval - elapsed + 0.1
                    self.total_waits += 1
                    total_wait += wait_time
                    logger.debug(f"最小间隔等待 {wait_time:.1f}s")
                    self._lock.release()
                    await asyncio.sleep(wait_time)
                    await self._lock.acquire()
                    now = time.monotonic()

            # 再次检查窗口
            cutoff = now - self.limit.period_seconds
            self._call_times = [t for t in self._call_times if t > cutoff]
            if len(self._call_times) >= self.limit.max_calls:
                self.total_throttled += 1
                raise RateLimitExceeded(
                    f"接口限流: 窗口{self.limit.period_seconds}s内已达{self.limit.max_calls}次上限"
                )

            self._call_times.append(now)
            self._last_call = now
            self.total_calls += 1

        return total_wait

    def remaining(self) -> int:
        """剩余可用次数"""
        now = time.monotonic()
        cutoff = now - self.limit.period_seconds
        active = sum(1 for t in self._call_times if t > cutoff)
        return max(0, self.limit.max_calls - active)

    def get_stats(self) -> dict:
        now = time.monotonic()
        cutoff = now - self.limit.period_seconds
        active = sum(1 for t in self._call_times if t > cutoff)
        return {
            "total_calls": self.total_calls,
            "window_calls": active,
            "remaining": max(0, self.limit.max_calls - active),
            "max_calls": self.limit.max_calls,
            "period_seconds": self.limit.period_seconds,
            "total_waits": self.total_waits,
            "total_throttled": self.total_throttled,
        }


class RateLimitExceeded(Exception):
    """限流异常"""
    pass


def calc_huawei_limits(station_count: int, device_counts: dict[int, int] | None = None) -> dict[str, EndpointLimit]:
    """
    根据华为电站和设备数量动态计算各接口限流配置。

    Args:
        station_count: 电站数量
        device_counts: 设备类型->数量的映射 {devTypeId: count}
                       例如 {1: 54, 47: 2, 62: 48}
    """
    if device_counts is None:
        device_counts = {}

    # 各类设备 ceil(数量/100) 之和
    sum_dev_100 = sum(math.ceil(c / 100) for c in device_counts.values()) if device_counts else 1
    # 各类设备 ceil(数量/10) 之和
    sum_dev_10 = sum(math.ceil(c / 10) for c in device_counts.values()) if device_counts else 3
    # 电站 ceil(数量/100)
    ceil_station_100 = math.ceil(station_count / 100) if station_count > 0 else 1

    return {
        # 登录: 每10分钟5次
        "login": EndpointLimit(max_calls=5, period_seconds=600),
        # 登出: 每10分钟5次
        "logout": EndpointLimit(max_calls=5, period_seconds=600),
        # 电站列表: 每天 ceil(N/100)*10+24 次 (用86400s)
        "getStationList": EndpointLimit(
            max_calls=ceil_station_100 * 10 + 24,
            period_seconds=86400,
            min_interval=60,
        ),
        # 电站实时: 每5分钟 ceil(N/100) 次, 并发1分钟1次
        "getStationRealKpi": EndpointLimit(
            max_calls=max(1, ceil_station_100),
            period_seconds=300,
            min_interval=60,
        ),
        # 电站日数据: 每天 ceil(N/100)+24 次, 并发1分钟1次
        "getKpiStationDay": EndpointLimit(
            max_calls=ceil_station_100 + 24,
            period_seconds=86400,
            min_interval=60,
        ),
        # 电站月数据: 同日数据
        "getKpiStationMonth": EndpointLimit(
            max_calls=ceil_station_100 + 24,
            period_seconds=86400,
            min_interval=60,
        ),
        # 电站年数据: 同日数据
        "getKpiStationYear": EndpointLimit(
            max_calls=ceil_station_100 + 24,
            period_seconds=86400,
            min_interval=60,
        ),
        # 电站小时数据
        "getKpiStationHour": EndpointLimit(
            max_calls=ceil_station_100 + 24,
            period_seconds=86400,
            min_interval=60,
        ),
        # 设备列表: 每天 ceil(站数/100)+24 次
        "getDevList": EndpointLimit(
            max_calls=ceil_station_100 + 24,
            period_seconds=86400,
        ),
        # 设备实时: 每5分钟 Σceil(各类设备数/100) 次
        "getDevRealKpi": EndpointLimit(
            max_calls=max(1, sum_dev_100),
            period_seconds=300,
        ),
        # 设备历史5min: 每天 Σceil(各类设备数/10)+24 次, 并发1分钟1次
        "getDevHistoryKpi": EndpointLimit(
            max_calls=sum_dev_10 + 24,
            period_seconds=86400,
            min_interval=60,
        ),
        # 设备日/月/年: 每天 Σceil(各类设备数/100)+24 次, 并发1分钟1次
        "getDevKpiDay": EndpointLimit(
            max_calls=sum_dev_100 + 24,
            period_seconds=86400,
            min_interval=60,
        ),
        # 告警: 每30分钟 MAX(ceil(站数/100), Σceil(各类设备数/100)) 次
        "getAlarmList": EndpointLimit(
            max_calls=max(ceil_station_100, sum_dev_100),
            period_seconds=1800,
        ),
        # 告警(历史): 每1小时1次
        "getAlarmData": EndpointLimit(
            max_calls=1,
            period_seconds=3600,
        ),
    }


class PlatformRateLimiter:
    """平台级限流管理器 - 管理一个平台下所有接口的限流"""

    def __init__(self, platform_name: str, default_limit: EndpointLimit | None = None):
        self.platform_name = platform_name
        self._endpoint_limiters: dict[str, EndpointLimiter] = {}
        self._global_limiter: EndpointLimiter | None = None
        if default_limit:
            self._global_limiter = EndpointLimiter(default_limit)

    def set_endpoint_limits(self, limits: dict[str, EndpointLimit]):
        """设置各接口的限流配置"""
        for endpoint, limit in limits.items():
            self._endpoint_limiters[endpoint] = EndpointLimiter(limit)

    async def acquire(self, endpoint: str = "") -> float:
        """
        获取调用许可。先检查全局限流，再检查接口限流。
        返回总等待时间（秒）。
        """
        total_wait = 0.0

        # 全局限流
        if self._global_limiter:
            total_wait += await self._global_limiter.acquire()

        # 接口级限流
        if endpoint and endpoint in self._endpoint_limiters:
            total_wait += await self._endpoint_limiters[endpoint].acquire()

        return total_wait

    def remaining(self, endpoint: str = "") -> int:
        """查询剩余可用次数"""
        if endpoint and endpoint in self._endpoint_limiters:
            return self._endpoint_limiters[endpoint].remaining()
        if self._global_limiter:
            return self._global_limiter.remaining()
        return 999

    def get_stats(self) -> dict:
        stats = {"platform": self.platform_name}
        if self._global_limiter:
            stats["global"] = self._global_limiter.get_stats()
        stats["endpoints"] = {
            name: limiter.get_stats()
            for name, limiter in self._endpoint_limiters.items()
        }
        return stats


class RateLimitManager:
    """全局限流管理 - 管理所有平台的限流器"""
    _platforms: dict[str, PlatformRateLimiter] = {}

    @classmethod
    def get_platform(cls, platform: str) -> PlatformRateLimiter:
        """获取平台限流器"""
        if platform not in cls._platforms:
            cls._platforms[platform] = PlatformRateLimiter(platform)
        return cls._platforms[platform]

    @classmethod
    def init_huawei(cls, station_count: int = 7,
                    device_counts: dict[int, int] | None = None) -> PlatformRateLimiter:
        """初始化华为限流器"""
        if device_counts is None:
            device_counts = {1: 54, 47: 2, 62: 48}  # 默认值来自文档

        limiter = cls.get_platform("huawei")
        limits = calc_huawei_limits(station_count, device_counts)
        limiter.set_endpoint_limits(limits)
        logger.info(f"华为限流器已初始化: {station_count}站, 设备{device_counts}")
        return limiter

    @classmethod
    def init_aiswei(cls) -> PlatformRateLimiter:
        """初始化爱士惟限流器 - 全局100次/分钟"""
        limiter = PlatformRateLimiter(
            "aiswei",
            default_limit=EndpointLimit(max_calls=100, period_seconds=60),
        )
        cls._platforms["aiswei"] = limiter
        logger.info("爱士惟限流器已初始化: 100次/分钟")
        return limiter

    @classmethod
    def init_sungrow(cls) -> PlatformRateLimiter:
        """初始化阳光电源限流器 - 保守默认值"""
        limiter = PlatformRateLimiter(
            "sungrow",
            default_limit=EndpointLimit(max_calls=30, period_seconds=60),
        )
        cls._platforms["sungrow"] = limiter
        logger.info("阳光电源限流器已初始化: 30次/分钟（保守值）")
        return limiter

    @classmethod
    def get_all_stats(cls) -> dict[str, dict]:
        return {name: p.get_stats() for name, p in cls._platforms.items()}

    @classmethod
    def reset(cls, platform: str | None = None):
        if platform:
            cls._platforms.pop(platform, None)
        else:
            cls._platforms.clear()
