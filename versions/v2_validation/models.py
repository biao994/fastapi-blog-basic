from typing import Dict, Optional
from datetime import datetime

from schemas import UserRegister, PostCreate

# ===== 内存存储 =====
users_db: Dict[int, dict] = {}
posts_db: Dict[int, dict] = {}
user_id_counter = 1
post_id_counter = 1

def get_next_user_id() -> int:
    """获取下一个用户ID"""
    global user_id_counter        # 1️⃣ 声明使用全局变量
    current_id = user_id_counter  # 2️⃣ 保存当前ID值
    user_id_counter += 1          # 3️⃣ ID计数器自增1，给下个用户用的
    return current_id             # 4️⃣ 返回这次分配的ID

def get_next_post_id() -> int:
    """获取下一个文章ID"""
    global post_id_counter
    current_id = post_id_counter
    post_id_counter += 1
    return current_id

# ===== 业务逻辑函数 =====

def create_user(user_data: UserRegister) -> dict:
    """创建用户"""
    
    user_id = get_next_user_id()
    user = {
        "id": user_id,
        "username": user_data.username,
        "email": user_data.email,
        "password": user_data.password,  # 实际项目中需要加密
        "created_at": datetime.now()
    }
    
    users_db[user_id] = user
    return user

def authenticate_user(username: str, password: str) -> Optional[dict]:
    """用户认证"""
    for user in users_db.values():
        if (user["username"] == username or user["email"] == username) and user["password"] == password:
            return user
    return None

def create_post(post_data: PostCreate, author_id: int) -> dict:
    """创建文章"""
    if author_id not in users_db:
        raise ValueError("用户不存在")
    
    post_id = get_next_post_id()
    post = {
        "id": post_id,
        "title": post_data.title,
        "content": post_data.content,
        "author_id": author_id,
        "author_name": users_db[author_id]["username"],
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    
    posts_db[post_id] = post
    return post

def get_user_by_id(user_id: int) -> Optional[dict]:
    """根据ID获取用户"""
    return users_db.get(user_id)

def get_post_by_id(post_id: int) -> Optional[dict]:
    """根据ID获取文章"""
    return posts_db.get(post_id)

def get_all_posts() -> list:
    """获取所有文章"""
    return list(posts_db.values())

def update_post(post_id: int, title: str, content: str) -> Optional[dict]:
    """更新文章"""
    if post_id not in posts_db:
        return None
    
    post = posts_db[post_id]
    post.update({
        "title": title,
        "content": content,
        "updated_at": datetime.now()
    })
    
    return post

def delete_post(post_id: int) -> bool:
    """删除文章"""
    if post_id not in posts_db:
        return False
    
    del posts_db[post_id]
    return True