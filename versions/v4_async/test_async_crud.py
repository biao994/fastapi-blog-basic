# test_async_crud.py
import asyncio
from database import AsyncSessionLocal, create_tables
import crud

async def test_async_crud():
    """测试异步CRUD操作"""
    # 创建数据表
    await create_tables()
    
    # 获取异步数据库会话
    async with AsyncSessionLocal() as db:
        try:
            # 测试异步创建用户
            user = await crud.create_user(
                db, 
                username="千两道化-巴基", 
                email="bj@qq.com", 
                password="MyPass136!"
            )
            print(f"异步创建用户成功: {user.username}")
            
            # 测试异步用户认证
            auth_user = await crud.authenticate_user(db, "千两道化-巴基", "MyPass136!")
            if auth_user:
                print(f"用户认证成功: {auth_user.username}")
            
            # 测试异步查询用户总数
            user_count = await crud.get_user_count(db)
            print(f"异步查询到 {user_count} 个用户")
            
        except Exception as e:
            print(f"异步测试失败: {e}")

# 运行异步测试
if __name__ == "__main__":
    asyncio.run(test_async_crud())