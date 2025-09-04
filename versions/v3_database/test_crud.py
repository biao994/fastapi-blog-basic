
from database import SessionLocal,create_tables
import crud

# 创建数据表

create_tables()

# 获取数据库会话
db = SessionLocal()

try:
    # 测试创建用户
    user = crud.create_user(
        db,
        username="火拳艾斯",
        email="aisi@qq.com",
        password="MyPass136!"
    )
    print(f"创建用户: {user}")

    # 测试创建文章
    post = crud.create_post(
        db,
        title="这个时代",
        content="这个时代就叫做白胡子时代吧！",
        author_id=user.id

    )

    # 测试获取文章
    posts = crud.get_all_posts(db)
    print(f"获取到的文章: {posts}")

except Exception as e:
    print(f"测试失败: {e}")
finally:
    db.close()