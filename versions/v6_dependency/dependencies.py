# v6_dependency/dependencies.py - 统一管理所有依赖
from fastapi import Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

# 从database.py移过来
from database import AsyncSessionLocal

async def get_async_db():
    """数据库会话依赖"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

def get_pagination(
    page: int = Query(1, ge=1, description="页码，从1开始"),
    size: int = Query(10, ge=1, le=100, description="每页数量，最大100")
):
    """分页参数依赖
    
    为什么用两套参数？
    - page/size：用户友好的参数（页码从1开始）
    - skip/limit：数据库友好的参数（偏移量从0开始）
    
    为什么用def而不是async def？
    - 这个函数只做数学计算，不涉及I/O操作
    - 同步函数性能更好，也更简洁
    """
    skip = (page - 1) * size  # 转换：第1页对应skip=0，第2页对应skip=10
    return {"skip": skip, "limit": size}





