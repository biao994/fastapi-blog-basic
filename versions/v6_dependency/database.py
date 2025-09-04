# v6_dependency/database.py - 只负责数据库配置
"""
异步数据库配置模块
配置异步SQLAlchemy和数据库连接
"""

import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# 异步数据库URL配置
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./blog_v4.db")


# 创建异步数据库引擎
async_engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # 设置为True，我们就可以看到执行的SQL语句了
    future=True
)


# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# 创建基础模型类
Base = declarative_base()


# 异步数据库初始化函数
async def create_tables():
    """异步创建所有数据表"""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
