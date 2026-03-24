"""初始化默认数据"""
from sqlalchemy import select

from app.database import async_session
from app.models.user import User
from app.dependencies import hash_password


async def init_default_data():
    """创建默认管理员账号"""
    async with async_session() as db:
        result = await db.execute(select(User).where(User.username == "admin"))
        if not result.scalar_one_or_none():
            admin = User(
                username="admin",
                password_hash=hash_password("admin123"),
                display_name="系统管理员",
                role="admin",
            )
            db.add(admin)
            await db.commit()
