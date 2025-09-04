# v7_jwt/dependencies.py
from fastapi import Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from database import AsyncSessionLocal
from auth import verify_token
import crud

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

security = HTTPBearer()

async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> int:
    token = credentials.credentials
    payload = verify_token(token)
    return payload["user_id"]

async def get_current_user(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_async_db)
):
    user = await crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="用户不存在"
        )
    return user

async def verify_post_owner(
    post_id: int,
    current_user_id: int = Depends(get_current_user_id),  # 先认证：从JWT获取用户ID
    db: AsyncSession = Depends(get_async_db)
):
    """验证文章所有权（权限依赖）
    
    自动检查：用户身份认证 → 文章存在性 → 所有权验证
    成功时返回文章对象，失败时抛出HTTP异常（401/403/404）
    """
    post = await crud.get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    if post.author_id != current_user_id:
        raise HTTPException(status_code=403, detail="只能操作自己的文章")
    
    return post  






