# v4_async/schemas.py
"""
博客系统v4.0 - API请求和响应模型
定义所有的Pydantic模型用于数据验证
"""
import re
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, validator


def validate_content_safety(content: str) -> str:
    # 定义敏感词列表（实际项目中应该从数据库或配置文件读取）
    banned_words = [
        '黑胡子','白胡子','茶胡子'
    ]

    content_lower = content.lower()
    for banned_word in banned_words:
        if banned_word in content_lower:
            raise ValueError(f'内容中包含敏感词: {banned_word}')
    return content



# ===== 请求模型 =====

class UserRegister(BaseModel):
    """用户注册模型"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱地址")
    password: str = Field(..., min_length=8, description="密码")
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    bio: Optional[str] = Field(None, max_length=200, description="个人简介")


    @validator('password')
    def validate_password_strength(cls, v):
        """验证密码强度"""
        # 检查大写字母
        if not re.search(r'[A-Z]',v):
            raise ValueError('密码必须包含一个至少一个大写字母')

        # 检查小写字母
        if not re.search(r'[a-z]',v):
            raise ValueError('密码必须包含至少一个小写字母')

        # 检查数字
        if not re.search(r'\d',v):
            raise ValueError('密码必须包含至少一个数字')

        # 检查特殊字符
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('密码必须包含至少一个特殊字符(!@#$%^&*等)')

        # 检查连续字符
        if re.search(r'(.)\1{2,}',v):
            raise ValueError('密码不能包含3个以上连续相同字符')

        if re.search(r'(012|123|234|345|456|567|678|789)', v):
            raise ValueError('密码不能包含连续数字')

        if re.search(r'(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)', v.lower()):
            raise ValueError('密码不能包含连续字母')
        
        return v 

    # 新增：邮箱域名验证
    @validator('email')
    def validate_email_domain(cls, v):
        """验证邮箱域名限制"""
        domain = v.split('@')[1].lower()
        allowed_domains = [
            'gmail.com', 'qq.com', '163.com', '126.com',
            'outlook.com', 'hotmail.com', 'sina.com'
        ]
        
        if domain not in allowed_domains:
            allowed_list = ', '.join(allowed_domains)
            raise ValueError(f'不支持的邮箱域名，请使用以下邮箱: {allowed_list}')
        
        return v

class UserLogin(BaseModel):
    """用户登录模型"""
    account: str = Field(..., description="用户名或邮箱")
    password: str = Field(..., description="密码")

class PostCreate(BaseModel):
    """文章创建模型"""
    title: str = Field(..., min_length=5, max_length=200, description="文章标题")
    content: str = Field(..., min_length=10, description="文章内容")

    @validator('title')
    def validate_title_safety(cls, v):
        """验证标题安全"""
        v = validate_content_safety(v)
        return v
    
    
    @validator('content')
    def validate_content_safety(cls, v):
        """验证内容安全"""
        v = validate_content_safety(v)
        if len(v) > 10000:
            raise ValueError('文章内容不能超过10000字')
        return v
    
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