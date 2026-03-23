import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "光伏电站监控平台"
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/gfdz.db"
    SYNC_DATABASE_URL: str = "sqlite:///./data/gfdz.db"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "gfdz-secret-key-change-in-production")
    # 数据同步间隔（分钟）
    SYNC_INTERVAL_MINUTES: int = 15
    # 调试模式
    DEBUG: bool = True


settings = Settings()
