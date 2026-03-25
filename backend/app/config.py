from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 数据库 — 单容器部署默认用 localhost
    DATABASE_URL: str = "postgresql+asyncpg://gfdz:gfdz123456@localhost:5432/gfdz"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    JWT_SECRET: str = "your-jwt-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440

    # 应用
    APP_NAME: str = "光伏电站监控平台"
    DEBUG: bool = True

    class Config:
        # 不读 .env 文件，只用环境变量，避免 .env 覆盖 docker-compose 配置
        extra = "ignore"


settings = Settings()
