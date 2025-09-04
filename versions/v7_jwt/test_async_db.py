import asyncio
from sqlalchemy import func, select
from database import create_tables, AsyncSessionLocal
from models import User, Post


async def test_async_datablse():
    await create_tables()
    # 验证异步数据库连接
    async with AsyncSessionLocal() as session:
        user_count = await session.scalar(
            select(func.count()).select_from(User)
        )

        post_count = await session.scalar(
            select(func.count()).select_from(Post)
        )
        
        
        print(f"异步数据库连接成功！用户表:{user_count}条记录，文章表:{post_count}条记录")

if __name__ == "__main__":
    asyncio.run(test_async_datablse())