# versions/v3_database/main.py
"""
博客系统v3.0 - 数据库版本
基于Day2的API，升级为数据库存储
"""

from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional

# 导入数据库相关
from database import get_db, create_tables
import crud

# 导入schemas（复用Day2的验证模型）
from schemas import UserRegister, UserResponse, UserLogin, PostCreate, PostResponse

# 创建数据表
create_tables()

app = FastAPI(
    title="博客系统API v3.0",
    description="7天FastAPI学习系列 - Day3数据库持久化版本",
    version="3.0.0"
)

# 全局变量：当前用户（Day6会用JWT替换）
current_user_id: Optional[int] = None

# ===== 根路由 =====

@app.get("/")
def root():
    """欢迎页面"""
    return {
        "message": "欢迎使用博客系统API v3.0",
        "version": "3.0.0",
        "docs": "/docs",
        "features": ["用户管理", "文章管理", "数据验证增强", "数据库持久化"],
        "next_version": "Day4将添加异步优化"
    }

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """健康检查"""
    user_count = crud.get_user_count(db)
    post_count = crud.get_post_count(db)
    
    return {
        "status": "healthy",
        "version": "3.0.0",
        "users_count": user_count,
        "posts_count": post_count,
        "database": "SQLite (生产环境建议使用PostgreSQL)"
    }

# ===== 用户相关API =====

@app.post("/users/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    """用户注册 - 数据库版本"""
    
    try:
        db_user = crud.create_user(
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建用户失败: {str(e)}")

@app.post("/users/login")
def login_user(login_data: UserLogin, db: Session = Depends(get_db)):
    """用户登录 - 数据库版本"""
    global current_user_id
    
    user = crud.authenticate_user(db, login_data.account, login_data.password)
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
def get_current_user(db: Session = Depends(get_db)):
    """获取当前用户信息"""
    if not current_user_id:
        raise HTTPException(status_code=401, detail="请先登录")
    
    user = crud.get_user_by_id(db, current_user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        created_at=user.created_at
    )

@app.get("/users", response_model=List[UserResponse])
def list_users(db: Session = Depends(get_db)):
    """获取用户列表"""
    users = crud.get_all_users(db)
    return [
        UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            created_at=user.created_at
        )
        for user in users
    ]

# ===== 文章相关API =====

@app.post("/posts", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_new_post(post_data: PostCreate, db: Session = Depends(get_db)):
    """发布文章"""
    if not current_user_id:
        raise HTTPException(status_code=401, detail="请先登录")
    
    try:
        db_post = crud.create_post(
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建文章失败: {str(e)}")

@app.get("/posts", response_model=List[PostResponse])
def list_posts(db: Session = Depends(get_db)):
    """获取文章列表"""
    posts = crud.get_all_posts(db)
    
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
def get_post(post_id: int, db: Session = Depends(get_db)):
    """获取文章详情"""
    post = crud.get_post_by_id(db, post_id)
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

@app.put("/posts/{post_id}", response_model=PostResponse)
def update_post(post_id: int, post_data: PostCreate, db: Session = Depends(get_db)):
    """更新文章"""
    if not current_user_id:
        raise HTTPException(status_code=401, detail="请先登录")
    
    post = crud.get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    if post.author_id != current_user_id:
        raise HTTPException(status_code=403, detail="只能编辑自己的文章")
    
    # 更新文章
    updated_post = crud.update_post(
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

@app.delete("/posts/{post_id}")
def delete_post(post_id: int, db: Session = Depends(get_db)):
    """删除文章"""
    if not current_user_id:
        raise HTTPException(status_code=401, detail="请先登录")
    
    post = crud.get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    if post.author_id != current_user_id:
        raise HTTPException(status_code=403, detail="只能删除自己的文章")
    
    success = crud.delete_post(db, post_id)
    if not success:
        raise HTTPException(status_code=500, detail="删除文章失败")
    
    return {"message": "文章删除成功"}