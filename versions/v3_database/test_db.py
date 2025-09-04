# 创建测试脚本 test_db.py
from database import create_tables, SessionLocal
from models import User, Post

# 创建数据表
create_tables()

# 验证数据库连接
db = SessionLocal()
try:
    user_count = db.query(User).count()
    post_count = db.query(Post).count()
    print(f"数据库连接成功！用户表:{user_count}条记录，文章表:{post_count}条记录")
finally:
    db.close()


