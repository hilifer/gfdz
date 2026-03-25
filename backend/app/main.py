"""光伏电站监控平台 — FastAPI 入口"""
import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base
from app.api import auth, dashboard, stations, devices, alarms, manufacturers, work_orders, system, data_query

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 等待数据库就绪，最多重试 30 次（约 30 秒）
    for attempt in range(1, 31):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("数据库连接成功，表已创建")
            break
        except Exception as e:
            logger.warning("数据库连接失败 (第%d次): %s", attempt, e)
            if attempt == 30:
                logger.error("数据库连接失败，放弃重试")
                raise
            await asyncio.sleep(1)
    # 初始化默认管理员
    from app.services.init_data import init_default_data
    await init_default_data()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version="2.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["总览"])
app.include_router(stations.router, prefix="/api/stations", tags=["电站"])
app.include_router(devices.router, prefix="/api/devices", tags=["设备"])
app.include_router(alarms.router, prefix="/api/alarms", tags=["告警"])
app.include_router(manufacturers.router, prefix="/api/manufacturers", tags=["厂家"])
app.include_router(work_orders.router, prefix="/api/work-orders", tags=["工单"])
app.include_router(system.router, prefix="/api/system", tags=["系统"])
app.include_router(data_query.router, prefix="/api/query", tags=["数据查询"])


@app.get("/api/health")
async def health():
    return {"status": "ok", "app": settings.APP_NAME}
