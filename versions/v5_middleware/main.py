# v5_middleware/main.py
"""
博客系统v5.0 - 中间件版本
添加CORS、日志等中间件支持
"""

from fastapi import FastAPI, HTTPException, Depends, status, Query,Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import logging
import time

# 导入Day4的模块
import crud
from database import get_async_db, create_tables
from schemas import UserRegister, UserResponse, UserLogin, PostCreate, PostResponse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="博客系统API v5.0",
    description="7天FastAPI学习系列 - Day5中间件版本",
    version="5.0.0"
)

# 添加CORS中间件 - 解决前端跨域问题
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",    # React开发服务器
        "http://127.0.0.1:3000",   # 本地访问
        "http://localhost:5173",   # Vite开发服务器
        "http://127.0.0.1:5173"    # Vite本地访问
    ],
    allow_credentials=True,  # 允许携带认证信息（cookies等）
    allow_methods=["*"],     # 允许所有HTTP方法
    allow_headers=["*"],     # 允许所有请求头
)

logger.info("CORS中间件已配置，支持前端跨域访问")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    
    """
    请求日志中间件
    记录每个请求的详细信息和处理时间
    """
    start_time = time.time()
    # 记录请求开始
    logger.info(
        "请求开始: %s %s - 客户端: %s",
        request.method, 
        request.url, 
        request.client.host if request.client else 'unknown'
    )

    # 处理请求
    response = await call_next(request)

    # 计算处理时间
    process_time = time.time() - start_time

    status_text ="成功" if response.status_code <400 else "失败"

    logger.info(
        "请求完成(%s): %s %s - 状态码: %d - 耗时: %.4f秒",
        status_text,
        request.method, 
        request.url, 
        response.status_code, 
        process_time
    )
    # 在响应头中添加处理时间（方便前端监控）
    response.headers["X-Process-Time"] = str(process_time)

    if process_time > 1:
        logger.warning(
            "慢请求警告: %s %s 耗时 %.4f秒，建议优化",
            request.method, 
            request.url, 
            process_time
        )

    return response

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    HTTP异常处理器
    统一处理所有HTTP异常，返回标准格式
    """
    logger.error(
        "HTTP异常: %d - %s - 请求: %s %s",
        exc.status_code,  
        exc.detail,       
        request.method,  
        request.url       
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "status_code": exc.status_code,
            "message": exc.detail,
            "path": request.url.path,
            "timestamp":time.time()
            }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    数据验证异常处理器
    处理Pydantic模型验证错误
    """
    error_messages = [error['msg'] for error in exc.errors()]
    logger.warning(
        "数据验证失败: %s - 请求: %s %s",
        error_messages,
        request.method, 
        request.url
    )

    return JSONResponse(
        status_code=422,
        content={
            "error": True,
            "status_code": 422,
            "message": "数据验证失败",
            "details": error_messages,  
            "path":str(request.url),
            "timestamp":time.time()
        }
    )

@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    """
    全局异常处理器
    处理所有未捕获的异常
    """
    logger.error(
        "未处理异常：%s: %s - 请求：%s %s",
        type(exc).__name__, 
        str(exc), 
        request.method, 
        request.url,
        exc_info=True        
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "status_code": 500,
            "message": "服务器内部错误",
            "path": str(request.url),
            "timestamp": time.time()
        }
    )

# 全局变量：当前用户（Day7会用JWT替换）
current_user_id: Optional[int] = None

# 应用启动时创建数据表
@app.on_event("startup")
async def startup_event():
    """应用启动时异步创建数据表"""
    await create_tables()
    logger.info("数据库表创建完成")

# ===== 根路由 =====

@app.get("/")
async def root():
    """欢迎页面"""
    logger.info("访问根路由")
    return {
        "message": "欢迎使用博客系统API v5.0",
        "version": "5.0.0",
        "docs": "/docs",
        "features": [
            "用户管理", 
            "文章管理", 
            "数据验证增强", 
            "数据库持久化", 
            "异步优化", 
            "CORS支持",
            "请求日志",
            "异常处理"
        ],
        "next_version": "Day6将添加依赖注入"
    }
@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_async_db)):
    """健康检查API"""
    try:
        user_count = await crud.get_user_count(db)
        post_count = await crud.get_post_count(db)
        
        logger.info("健康检查通过：用户数=%d, 文章数=%d", user_count, post_count)
        
        return {
            "status": "healthy",
            "version": "5.0.0",
            "users_count": user_count,
            "posts_count": post_count,
            "database": "SQLite with async support",
            "middleware": "CORS、日志、异常处理",
            "performance": "异步优化已启用"
        }
    except Exception as e:
        logger.error("健康检查失败：%s", str(e))
        raise HTTPException(status_code=503, detail="服务不可用")

# ===== 异步用户相关API =====

@app.post("/users/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserRegister, db: AsyncSession = Depends(get_async_db)):
    """异步用户注册"""

    logger.info("用户注册请求： 用户名=%s,邮箱=%s", user_data.username, user_data.email)
    
    try:
        db_user = await crud.create_user(
            db, 
            username=user_data.username,
            email=user_data.email,
            password=user_data.password
        )
        logger.info("用户注册成功: ID=%d, 用户名=%s", db_user.id, db_user.username)
        
        return UserResponse(
            id=db_user.id,
            username=db_user.username,
            email=db_user.email,
            created_at=db_user.created_at
        )
    except ValueError as e:
        logger.warning("用户注册失败: %s - 用户名=%s", str(e), user_data.username)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("用户注册异常: %s - 用户名=%s", str(e), user_data.username)
        raise HTTPException(status_code=500, detail=f"创建用户失败: {str(e)}")

@app.post("/users/login")
async def login_user(login_data: UserLogin, db: AsyncSession = Depends(get_async_db)):
    """异步用户登录"""
    logger.info("用户登录请求： 账户=%s", login_data.account)

    global current_user_id
    
    user = await crud.authenticate_user(db, login_data.account, login_data.password)
    if not user:
        logger.warning("登录失败: 账号或密码错误 - 账号=%s", login_data.account)
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    current_user_id = user.id
    logger.info("用户登录成功: ID=%d, 用户名=%s", user.id, user.username)

    return {
        "message": "登录成功",
        "user": UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            created_at=user.created_at
        )
    }

@app.get("/users/profile", response_model=UserResponse)
async def get_current_user(db: AsyncSession = Depends(get_async_db)):
    """异步获取当前用户信息"""
    if not current_user_id:
        raise HTTPException(status_code=401, detail="请先登录")
    
    user = await crud.get_user_by_id(db, current_user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        created_at=user.created_at
    )

@app.get("/users", response_model=List[UserResponse])
async def list_users(db: AsyncSession = Depends(get_async_db)):
    """异步获取用户列表"""
    users = await crud.get_all_users(db)
    return [
        UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            created_at=user.created_at
        )
        for user in users
    ]

# ===== 异步文章相关API =====

@app.post("/posts", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post_api(post_data: PostCreate, db: AsyncSession = Depends(get_async_db)):
    """异步创建文章"""
    if not current_user_id:
        raise HTTPException(status_code=401, detail="请先登录")
    
    try:
        db_post = await crud.create_post(
            db,
            title=post_data.title,
            content=post_data.content,
            author_id=current_user_id
        )
        
        return PostResponse(
            id=db_post.id,
            title=db_post.title,
            content=db_post.content,
            author_id=db_post.author_id,
            created_at=db_post.created_at,
            updated_at=db_post.updated_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建文章失败: {str(e)}")

@app.get("/posts", response_model=List[PostResponse])
async def list_posts(
    skip: int = Query(0, ge=0, description="跳过的条数"), 
    limit: int = Query(10, ge=1, le=100, description="每页条数"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    db: AsyncSession = Depends(get_async_db)
):
    """异步获取文章列表（支持分页）"""
    posts = await crud.get_posts(db, skip=skip, limit=limit,keyword=keyword)
    return [
        PostResponse(
            id=post.id,
            title=post.title,
            content=post.content,
            author_id=post.author_id,
            created_at=post.created_at,
            updated_at=post.updated_at
        )
        for post in posts
    ]

@app.get("/posts/{post_id}", response_model=PostResponse)
async def get_post(post_id: int, db: AsyncSession = Depends(get_async_db)):
    """异步获取单篇文章"""
    post = await crud.get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    return PostResponse(
        id=post.id,
        title=post.title,
        content=post.content,
        author_id=post.author_id,
        created_at=post.created_at,
        updated_at=post.updated_at
    )

@app.get("/users/{user_id}/posts", response_model=List[PostResponse])
async def get_user_posts(user_id: int, db: AsyncSession = Depends(get_async_db)):
    """异步获取指定用户的所有文章"""
    # 检查用户是否存在
    user = await crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    posts = await crud.get_posts_by_user(db, user_id)
    return [
        PostResponse(
            id=post.id,
            title=post.title,
            content=post.content,
            author_id=post.author_id,
            created_at=post.created_at,
            updated_at=post.updated_at
        )
        for post in posts
    ]

@app.put("/posts/{post_id}", response_model=PostResponse)
async def update_post_api(post_id: int, post_data: PostCreate, db: AsyncSession = Depends(get_async_db)):
    """异步更新文章"""
    if not current_user_id:
        raise HTTPException(status_code=401, detail="请先登录")
    
    post = await crud.get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    if post.author_id != current_user_id:
        raise HTTPException(status_code=403, detail="只能编辑自己的文章")
    
    try:
        updated_post = await crud.update_post(
            db, 
            post_id, 
            title=post_data.title, 
            content=post_data.content
        )
        
        return PostResponse(
            id=updated_post.id,
            title=updated_post.title,
            content=updated_post.content,
            author_id=updated_post.author_id,
            created_at=updated_post.created_at,
            updated_at=updated_post.updated_at
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新文章失败: {str(e)}")

@app.delete("/posts/{post_id}")
async def delete_post_api(post_id: int, db: AsyncSession = Depends(get_async_db)):
    """异步删除文章"""
    if not current_user_id:
        raise HTTPException(status_code=401, detail="请先登录")
    
    post = await crud.get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    if post.author_id != current_user_id:
        raise HTTPException(status_code=403, detail="只能删除自己的文章")
    
    success = await crud.delete_post(db, post_id)
    if not success:
        raise HTTPException(status_code=500, detail="删除文章失败")
    
    return {"message": "文章删除成功"}