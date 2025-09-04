# v1_basic/schemas.py
"""
博客系统v1.0 - API请求和响应模型
定义所有的Pydantic模型用于数据验证
"""
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr

# ===== 请求模型 =====

class UserRegister(BaseModel):
    """用户注册模型 """
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱地址")
    password: str = Field(..., min_length=8, description="密码")

class UserLogin(BaseModel):
    """用户登录模型"""
    account: str = Field(..., description="用户名或邮箱")
    password: str = Field(..., description="密码")

class PostCreate(BaseModel):
    """文章创建模型"""
    title: str = Field(..., min_length=5, max_length=200, description="文章标题")
    content: str = Field(..., min_length=10, description="文章内容")

# ===== 响应模型 =====

class UserResponse(BaseModel):
    """用户响应模型"""
    id: int
    username: str
    email: str
    created_at: datetime

class PostResponse(BaseModel):
    """文章响应模型"""
    id: int
    title: str
    content: str
    author_id: int
    created_at: datetime
    updated_at: datetime