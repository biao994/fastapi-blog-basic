# versions/v4_async/crud.py
"""
异步数据库CRUD操作
封装所有异步数据库访问逻辑
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, desc
from typing import List, Optional
import hashlib

from models import User, Post

# ===== 异步用户相关操作 =====

async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    """异步根据ID获取用户"""
    result = await db.execute(select(User).filter(User.id == user_id))
    return result.scalar_one_or_none()

async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """异步根据用户名获取用户"""
    result = await db.execute(select(User).filter(User.username == username))
    return result.scalar_one_or_none()

async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """异步根据邮箱获取用户"""
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalar_one_or_none()

async def get_user_count(db: AsyncSession) -> int:
    """异步获取用户总数"""
    result = await db.execute(select(User))
    users = result.scalars().all()
    return len(users)

async def get_all_users(db: AsyncSession) -> List[User]:
    """异步获取所有用户"""
    result = await db.execute(select(User))
    return result.scalars().all()

async def create_user(db: AsyncSession, username: str, email: str, password: str) -> User:
    """异步创建用户"""
    # 检查用户名是否已存在
    existing_user = await get_user_by_username(db, username)
    if existing_user:
        raise ValueError("用户名已存在")
    
    # 检查邮箱是否已被注册
    existing_email = await get_user_by_email(db, email)
    if existing_email:
        raise ValueError("邮箱已被注册")
    
    # 密码哈希
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    db_user = User(
        username=username,
        email=email,
        hashed_password=hashed_password
    )
    
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    
    return db_user

async def authenticate_user(db: AsyncSession, account: str, password: str) -> Optional[User]:
    """异步用户认证 - 支持用户名或邮箱登录"""
    # 支持用户名或邮箱登录
    result = await db.execute(
        select(User).filter(
            or_(User.username == account, User.email == account)
        )
    )
    user = result.scalar_one_or_none()
    
    if not user:
        return None
    
    # 验证密码
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    if user.hashed_password != password_hash:
        return None
    
    return user

# ===== 异步文章相关操作 =====

async def get_post_by_id(db: AsyncSession, post_id: int) -> Optional[Post]:
    """异步根据ID获取文章"""
    result = await db.execute(select(Post).filter(Post.id == post_id))
    return result.scalar_one_or_none()

async def get_posts_by_user(db: AsyncSession, user_id: int) -> List[Post]:
    """异步获取指定用户的所有文章"""
    result = await db.execute(
        select(Post).filter(Post.author_id == user_id).order_by(desc(Post.created_at))
    )
    return result.scalars().all()

async def get_posts(db: AsyncSession, skip: int = 0, limit: int = 100, keyword: str= None) -> List[Post]:
    """异步获取文章列表（支持分页和搜索）"""
    query = select(Post)

    if keyword and keyword.strip():
        query = query.filter(
            or_(
                Post.title.contains(keyword),
                Post.content.contains(keyword)
            )
        )
    
    query = query.order_by(desc(Post.created_at)).offset(skip).limit(limit)
        
    result = await db.execute(query)
    return result.scalars().all()

async def get_post_count(db: AsyncSession) -> int:
    """异步获取文章总数"""
    result = await db.execute(select(Post))
    posts = result.scalars().all()
    return len(posts)

async def create_post(db: AsyncSession, title: str, content: str, author_id: int) -> Post:
    """异步创建文章"""
    # 验证作者是否存在
    author = await get_user_by_id(db, author_id)
    if not author:
        raise ValueError("作者不存在")
    
    db_post = Post(
        title=title,
        content=content,
        author_id=author_id
    )
    
    db.add(db_post)
    await db.commit()
    await db.refresh(db_post)
    
    return db_post

async def update_post(db: AsyncSession, post_id: int, title: str = None, content: str = None) -> Optional[Post]:
    """异步更新文章"""
    post = await get_post_by_id(db, post_id)
    if not post:
        return None
    
    if title is not None:
        post.title = title
    if content is not None:
        post.content = content
    
    await db.commit()
    await db.refresh(post)
    
    return post

async def delete_post(db: AsyncSession, post_id: int) -> bool:
    """异步删除文章"""
    post = await get_post_by_id(db, post_id)
    if not post:
        return False
    
    await db.delete(post)
    await db.commit()
    
    return True