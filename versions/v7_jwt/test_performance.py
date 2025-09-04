# performance_test.py
import asyncio
import aiohttp
import time
import requests

async def async_test_request(session, url):
    """异步请求测试"""
    async with session.get(url) as response:
        return await response.json()

async def async_performance_test():
    """异步性能测试"""
    url = "http://localhost:8000/health"  # Day4异步版本
    start_time = time.time()
    
    async with aiohttp.ClientSession() as session:
        tasks = [async_test_request(session, url) for _ in range(1000)]
        results = await asyncio.gather(*tasks)
    
    end_time = time.time()
    print(f"异步版本（Day4）：1000个请求耗时 {end_time - start_time:.2f} 秒")

def sync_performance_test():
    """同步性能测试"""
    url = "http://localhost:8001/health"  # Day3同步版本
    start_time = time.time()
    
    for _ in range(1000):
        response = requests.get(url)
        result = response.json()
    
    end_time = time.time()
    print(f"同步版本（Day3）：1000个请求耗时 {end_time - start_time:.2f} 秒")

if __name__ == "__main__":
    print("开始性能对比测试...")
    
    # 测试异步版本
    asyncio.run(async_performance_test())
    
    # 测试同步版本
    sync_performance_test()