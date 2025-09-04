
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc
import hashlib
from models import User, Post
from typing import List, Optional
# ===== 用户相关操作 =====

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_count(db: Session):
    return db.query(User).count()

def get_all_users(db: Session):
    return db.query(User).all()


def create_user(db: Session,username:str,email:str,password:str):

    # 检查用户名是否已存在
    if get_user_by_username(db, username):
        raise ValueError("用户名已存在")
    
    # 检查邮箱是否已被注册
    if get_user_by_email(db, email):
        raise ValueError("邮箱已被注册")
    
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    db_user = User(username=username,email=email,hashed_password=hashed_password)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

def authenticate_user(db: Session, account: str, password: str):
    user = db.query(User).filter(
        or_(User.username == account, User.email == account)
    ).first()

    if not user:
        return None

    password_hash = hashlib.sha256(password.encode()).hexdigest()
    if user.hashed_password != password_hash:
        return None
    
    return user

def create_post(db: Session, title:str, content:str, author_id:int) -> Post:
    
    user = db.query(User).filter(
        or_(User.id == author_id)
    ).first()

    if not user:
        raise ValueError("用户不存在")
    
    db_post = Post(title=title, content=content, author_id=author_id)

    db.add(db_post)
    db.commit()
    db.refresh(db_post)

    return db_post

def get_all_posts(db: Session) -> List[Post]:
    return db.query(Post).order_by(desc(Post.created_at)).all()

def get_post_by_id(db: Session, post_id: int) -> Post:
    return db.query(Post).filter(Post.id == post_id).first()

def get_post_count(db: Session):
    return db.query(Post).count()

def update_post(db: Session, post_id: int, title: str, content: str) -> Optional[Post]:
    post = db.query(Post).filter(Post.id == post_id).first()

    if not post:
        return None
    
    post.title = title
    post.content = content

    db.commit()
    db.refresh(post)

    return post

def delete_post(db: Session, post_id: int) -> bool:
    """删除文章"""
    post = get_post_by_id(db, post_id)
    if not post:
        return False
    
    db.delete(post)
    db.commit()
    return True
