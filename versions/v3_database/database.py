# versions/v3_database/database.py
"""
数据库配置模块
配置SQLAlchemy和数据库连接
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 数据库URL配置
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./blog_v3.db")

# 创建数据库引擎
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False  # 设置为True，我们就可以看到执行的SQL语句了
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基础模型类
Base = declarative_base()

# 依赖注入：获取数据库会话
def get_db():
    """
    获取数据库会话的依赖注入函数
    使用yield确保会话正确关闭
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 数据库初始化函数
def create_tables():
    """创建所有数据表"""
    Base.metadata.create_all(bind=engine)
