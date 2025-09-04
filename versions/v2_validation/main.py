# v2_validation/main.py
"""
博客系统v2.0 - FastAPI主应用
Day2: 数据验证增强版本，基于Day1升级
"""

from fastapi import FastAPI, HTTPException, status
from typing import List, Optional

from schemas import UserRegister, UserLogin, UserResponse, PostCreate, PostResponse
from models import (
    create_user, authenticate_user, create_post, 
    get_user_by_id, get_post_by_id, get_all_posts,
    update_post, delete_post,  
    users_db, posts_db
)

# 创建FastAPI应用
app = FastAPI(
    title="博客系统API v2.0",
    description="7天FastAPI学习系列 - Day2数据验证增强版本",
    version="2.0.0"
)

# 全局变量：简单的登录状态管理（Day6会用JWT替换）
current_user_id: Optional[int] = None

# ===== 根路由 =====

@app.get("/")
def root():
    """欢迎页面"""
    return {
        "message": "欢迎使用博客系统API v2.0",
        "version": "2.0.0",
        "docs": "/docs",
        "features": ["用户管理", "文章管理", "数据验证增强"],
        "next_version": "Day3将添加数据库持久化"
    }

@app.get("/health")
def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "users_count": len(users_db),
        "posts_count": len(posts_db)
    }

# ===== 用户管理API =====

@app.post("/users/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserRegister):
    """
    用户注册
    
    - **username**: 用户名（3-50字符）
    - **email**: 邮箱地址
    - **password**: 密码（至少8字符）
    """
    try:
        user = create_user(user_data)
        return UserResponse(
            id=user["id"],
            username=user["username"],
            email=user["email"],
            created_at=user["created_at"]
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/users/login")
def login_user(login_data: UserLogin):
    """
    用户登录
    
    - **username**: 用户名或邮箱
    - **password**: 密码
    """
    global current_user_id
    
    user = authenticate_user(login_data.account, login_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="用户名或密码错误"
        )
    
    current_user_id = user["id"]
    
    return {
        "message": "登录成功",
        "user": UserResponse(
            id=user["id"],
            username=user["username"],
            email=user["email"],
            created_at=user["created_at"]
        )
    }

@app.get("/users/profile", response_model=UserResponse)
def get_current_user():
    """获取当前用户信息"""
    if not current_user_id:
        raise HTTPException(status_code=401, detail="请先登录")
    
    user = get_user_by_id(current_user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return UserResponse(
        id=user["id"],
        username=user["username"],
        email=user["email"],
        created_at=user["created_at"]
    )

@app.get("/users", response_model=List[UserResponse])
def list_users():
    """获取用户列表"""
    return [
        UserResponse(
            id=user["id"],
            username=user["username"],
            email=user["email"],
            created_at=user["created_at"]
        )
        for user in users_db.values()
    ]

# ===== 文章管理API =====

@app.post("/posts", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_new_post(post_data: PostCreate):
    """
    发布文章
    
    需要先登录
    """
    if not current_user_id:
        raise HTTPException(status_code=401, detail="请先登录")
    
    try:
        post = create_post(post_data, current_user_id)
        return PostResponse(**post)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/posts", response_model=List[PostResponse])
def list_posts():
    """获取文章列表"""
    posts = get_all_posts()
    return [PostResponse(**post) for post in posts]

@app.get("/posts/{post_id}", response_model=PostResponse)
def get_post(post_id: int):
    """获取文章详情"""
    post = get_post_by_id(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    return PostResponse(**post)

@app.put("/posts/{post_id}", response_model=PostResponse)
def update_post_endpoint(post_id: int, post_data: PostCreate):
    """更新文章"""
    if not current_user_id:
        raise HTTPException(status_code=401, detail="请先登录")
    
    post = get_post_by_id(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    if post["author_id"] != current_user_id:
        raise HTTPException(status_code=403, detail="只能编辑自己的文章")
    
    updated_post = update_post(post_id, post_data.title, post_data.content)
    if not updated_post:
        raise HTTPException(status_code=500, detail="更新文章失败")
    
    return PostResponse(**updated_post)

@app.delete("/posts/{post_id}")
def delete_post_endpoint(post_id: int):
    """删除文章"""
    if not current_user_id:
        raise HTTPException(status_code=401, detail="请先登录")
    
    post = get_post_by_id(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    if post["author_id"] != current_user_id:
        raise HTTPException(status_code=403, detail="只能删除自己的文章")
    
    success = delete_post(post_id)
    if not success:
        raise HTTPException(status_code=500, detail="删除文章失败")
    
    return {"message": "文章删除成功"}