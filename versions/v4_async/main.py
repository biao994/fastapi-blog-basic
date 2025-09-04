# versions/v4_async/main.py
"""
博客系统v4.0 - 异步版本
基于Day3的API，升级为异步操作
"""

from fastapi import FastAPI, HTTPException, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

# 导入异步数据库相关
from database import get_async_db, create_tables
import crud

# 导入schemas（复用Day3的验证模型）
from schemas import UserRegister, UserResponse, UserLogin, PostCreate, PostResponse

app = FastAPI(
    title="博客系统API v4.0",
    description="7天FastAPI学习系列 - Day4异步优化版本",
    version="4.0.0"
)

# 全局变量：当前用户（Day6会用JWT替换）
current_user_id: Optional[int] = None

# 应用启动时创建数据表
@app.on_event("startup")
async def startup_event():
    """应用启动时异步创建数据表"""
    await create_tables()

# ===== 根路由 =====

@app.get("/")
async def root():
    """异步欢迎页面"""
    return {
        "message": "欢迎使用博客系统API v4.0",
        "version": "4.0.0",
        "docs": "/docs",
        "features": ["用户管理", "文章管理", "数据验证增强", "数据库持久化", "异步优化"],
        "next_version": "Day5将添加架构重构"
    }

@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_async_db)):
    """异步健康检查"""
    user_count = await crud.get_user_count(db)
    post_count = await crud.get_post_count(db)
    
    return {
        "status": "healthy",
        "version": "4.0.0",
        "users_count": user_count,
        "posts_count": post_count,
        "database": "SQLite with async support",
        "performance": "异步优化已启用"
    }

# ===== 异步用户相关API =====

@app.post("/users/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserRegister, db: AsyncSession = Depends(get_async_db)):
    """异步用户注册"""
    try:
        db_user = await crud.create_user(
            db, 
            username=user_data.username,
            email=user_data.email,
            password=user_data.password
        )
        
        return UserResponse(
            id=db_user.id,
            username=db_user.username,
            email=db_user.email,
            created_at=db_user.created_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建用户失败: {str(e)}")

@app.post("/users/login")
async def login_user(login_data: UserLogin, db: AsyncSession = Depends(get_async_db)):
    """异步用户登录"""
    global current_user_id
    
    user = await crud.authenticate_user(db, login_data.account, login_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    current_user_id = user.id
    
    return {
        "message": "登录成功",
        "user": UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            created_at=user.created_at
        )
    }

@app.get("/users/profile", response_model=UserResponse)
async def get_current_user(db: AsyncSession = Depends(get_async_db)):
    """异步获取当前用户信息"""
    if not current_user_id:
        raise HTTPException(status_code=401, detail="请先登录")
    
    user = await crud.get_user_by_id(db, current_user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        created_at=user.created_at
    )

@app.get("/users", response_model=List[UserResponse])
async def list_users(db: AsyncSession = Depends(get_async_db)):
    """异步获取用户列表"""
    users = await crud.get_all_users(db)
    return [
        UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            created_at=user.created_at
        )
        for user in users
    ]

# ===== 异步文章相关API =====

@app.post("/posts", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post_api(post_data: PostCreate, db: AsyncSession = Depends(get_async_db)):
    """异步创建文章"""
    if not current_user_id:
        raise HTTPException(status_code=401, detail="请先登录")
    
    try:
        db_post = await crud.create_post(
            db,
            title=post_data.title,
            content=post_data.content,
            author_id=current_user_id
        )
        
        return PostResponse(
            id=db_post.id,
            title=db_post.title,
            content=db_post.content,
            author_id=db_post.author_id,
            created_at=db_post.created_at,
            updated_at=db_post.updated_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建文章失败: {str(e)}")

@app.get("/posts", response_model=List[PostResponse])
async def list_posts(
    skip: int = Query(0, ge=0, description="跳过的条数"), 
    limit: int = Query(10, ge=1, le=100, description="每页条数"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    db: AsyncSession = Depends(get_async_db)
):
    """异步获取文章列表（支持分页）"""
    posts = await crud.get_posts(db, skip=skip, limit=limit,keyword=keyword)
    return [
        PostResponse(
            id=post.id,
            title=post.title,
            content=post.content,
            author_id=post.author_id,
            created_at=post.created_at,
            updated_at=post.updated_at
        )
        for post in posts
    ]

@app.get("/posts/{post_id}", response_model=PostResponse)
async def get_post(post_id: int, db: AsyncSession = Depends(get_async_db)):
    """异步获取单篇文章"""
    post = await crud.get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    return PostResponse(
        id=post.id,
        title=post.title,
        content=post.content,
        author_id=post.author_id,
        created_at=post.created_at,
        updated_at=post.updated_at
    )

@app.get("/users/{user_id}/posts", response_model=List[PostResponse])
async def get_user_posts(user_id: int, db: AsyncSession = Depends(get_async_db)):
    """异步获取指定用户的所有文章"""
    # 检查用户是否存在
    user = await crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    posts = await crud.get_posts_by_user(db, user_id)
    return [
        PostResponse(
            id=post.id,
            title=post.title,
            content=post.content,
            author_id=post.author_id,
            created_at=post.created_at,
            updated_at=post.updated_at
        )
        for post in posts
    ]

@app.put("/posts/{post_id}", response_model=PostResponse)
async def update_post_api(post_id: int, post_data: PostCreate, db: AsyncSession = Depends(get_async_db)):
    """异步更新文章"""
    if not current_user_id:
        raise HTTPException(status_code=401, detail="请先登录")
    
    post = await crud.get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    if post.author_id != current_user_id:
        raise HTTPException(status_code=403, detail="只能编辑自己的文章")
    
    try:
        updated_post = await crud.update_post(
            db, 
            post_id, 
            title=post_data.title, 
            content=post_data.content
        )
        
        return PostResponse(
            id=updated_post.id,
            title=updated_post.title,
            content=updated_post.content,
            author_id=updated_post.author_id,
            created_at=updated_post.created_at,
            updated_at=updated_post.updated_at
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新文章失败: {str(e)}")

@app.delete("/posts/{post_id}")
async def delete_post_api(post_id: int, db: AsyncSession = Depends(get_async_db)):
    """异步删除文章"""
    if not current_user_id:
        raise HTTPException(status_code=401, detail="请先登录")
    
    post = await crud.get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    if post.author_id != current_user_id:
        raise HTTPException(status_code=403, detail="只能删除自己的文章")
    
    success = await crud.delete_post(db, post_id)
    if not success:
        raise HTTPException(status_code=500, detail="删除文章失败")
    
    return {"message": "文章删除成功"}