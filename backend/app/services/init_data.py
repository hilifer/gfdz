"""初始化默认数据"""
import json
import logging

from sqlalchemy import select

from app.database import async_session
from app.models.user import User
from app.models.manufacturer import Manufacturer
from app.dependencies import hash_password

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# 默认厂家配置
# ---------------------------------------------------------------------------

_DEFAULT_MANUFACTURERS = [
    {
        "code": "huawei",
        "name": "华为FusionSolar",
        "api_base_url": "https://intl.fusionsolar.huawei.com",
        "auth_config": {
            "userName": "YRKJAPI",
            "systemCode": "huawei666",
        },
    },
    {
        "code": "aiswei",
        "name": "爱士惟",
        "api_base_url": "https://api.aisweicloud.com",
        "auth_config": {
            "token": "R3dBOTVXeUdGRDBTTmJvMjZyNDF0QT09",
            "key": "204929444",
            "secret": "S9eyOBeTqUn56eAn5XovdjbDVMef6lRE",
        },
    },
    {
        "code": "sungrow",
        "name": "阳光电源",
        "api_base_url": "https://gateway.isolarcloud.com",
        "auth_config": {
            "appkey": "C37DA83CA621494DAF1859221169CDC9",
            "secret": "2557u433bmvnuwk61jrxr722xhnc81ug",
            "username": "yrkj_nibian",
            "password": "yr@123456",
        },
    },
    {
        "code": "solis",
        "name": "锦浪Solis",
        "api_base_url": "https://api.ginlong.com:13333",
        "auth_config": {
            "api_id": "1300386381677083058",
            "api_secret": "64ca50287e5e446988f6828ce4b16450",
        },
    },
]


async def init_default_data():
    """创建默认管理员账号和厂家数据"""
    try:
        async with async_session() as db:
            # ----- 默认管理员 -----
            result = await db.execute(select(User).where(User.username == "admin"))
            if not result.scalar_one_or_none():
                admin = User(
                    username="admin",
                    password_hash=hash_password("admin123"),
                    display_name="系统管理员",
                    role="admin",
                )
                db.add(admin)
                logger.info("已创建默认管理员账号: admin")

            # ----- 默认厂家 -----
            for mfr_cfg in _DEFAULT_MANUFACTURERS:
                existing = await db.execute(
                    select(Manufacturer).where(Manufacturer.code == mfr_cfg["code"])
                )
                if existing.scalar_one_or_none():
                    logger.debug("厂家已存在，跳过: %s", mfr_cfg["code"])
                    continue

                manufacturer = Manufacturer(
                    code=mfr_cfg["code"],
                    name=mfr_cfg["name"],
                    api_base_url=mfr_cfg["api_base_url"],
                    auth_config=json.dumps(mfr_cfg["auth_config"], ensure_ascii=False),
                    is_active=True,
                )
                db.add(manufacturer)
                logger.info("已创建厂家: %s (%s)", mfr_cfg["name"], mfr_cfg["code"])

            await db.commit()
    except Exception as exc:
        logger.error("初始化默认数据失败: %s", exc, exc_info=True)
