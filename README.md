# FastAPI 博客系统 - 基础教程

一个完整的 FastAPI 博客系统实现，通过 7 天渐进式学习，从基础搭建到 JWT 认证的完整开发过程。

## 📚 教程系列

本项目配套完整的博客教程系列[7天入门FastAPI后端开发](https://blog.csdn.net/weixin_46253270/category_13035817.html)，详细讲解每个版本的实现过程：

- **Day1**: 基础搭建 - FastAPI 项目初始化和基本 API
- **Day2**: 数据验证增强 - Pydantic 模型和输入验证
- **Day3**: 数据持久化 - SQLAlchemy 数据库集成
- **Day4**: 异步优化 - 异步数据库操作和性能提升
- **Day5**: 中间件系统 - CORS、日志记录和异常处理
- **Day6**: 依赖注入 - FastAPI 依赖系统和代码组织
- **Day7**: JWT 认证 - 用户认证和权限控制

## 🚀 项目特性

### 核心功能
- ✅ 用户注册和登录
- ✅ 文章创建、编辑、删除
- ✅ 文章列表和详情查看
- ✅ 用户个人资料管理

### 技术特性
- ✅ **数据验证**: Pydantic 模型验证
- ✅ **数据库**: SQLAlchemy ORM + SQLite
- ✅ **异步支持**: 全异步数据库操作
- ✅ **中间件**: CORS、日志、异常处理
- ✅ **依赖注入**: 模块化代码组织
- ✅ **JWT 认证**: 安全的用户认证系统
- ✅ **API 文档**: 自动生成的 Swagger 文档

## 📁 项目结构

```
fastapi-blog-basic/
├── versions/                    # 各版本实现
│   ├── v1_basic/               # Day1: 基础搭建
│   ├── v2_validation/          # Day2: 数据验证增强
│   ├── v3_database/            # Day3: 数据持久化
│   ├── v4_async/               # Day4: 异步优化
│   ├── v5_middleware/          # Day5: 中间件系统
│   ├── v6_dependency/          # Day6: 依赖注入
│   └── v7_jwt/                 # Day7: JWT 认证
├── README.md                   # 项目说明
└── LICENSE                     # 开源协议
```

## 🛠️ 技术栈

- **Web 框架**: FastAPI
- **数据库**: SQLite + SQLAlchemy
- **数据验证**: Pydantic
- **认证**: JWT (JSON Web Tokens)
- **异步支持**: asyncio + aiosqlite
- **API 文档**: Swagger UI (自动生成)

## 📖 版本说明

### v1_basic - 基础搭建
- FastAPI 应用初始化
- 基本的用户和文章 API
- 内存数据存储
- 简单的数据模型

### v2_validation - 数据验证增强
- Pydantic 数据验证模型
- 输入数据校验和错误处理
- API 文档完善
- 响应模型标准化

### v3_database - 数据持久化
- SQLAlchemy ORM 集成
- SQLite 数据库存储
- 数据库模型定义
- CRUD 操作实现

### v4_async - 异步优化
- 异步数据库操作
- 性能优化
- 分页和搜索功能
- 异步会话管理

### v5_middleware - 中间件系统
- CORS 跨域支持
- 请求日志记录
- 全局异常处理
- 统一错误响应格式

### v6_dependency - 依赖注入
- FastAPI 依赖系统
- 代码模块化组织
- 分页参数依赖
- 数据库会话依赖

### v7_jwt - JWT 认证
- JWT token 生成和验证
- 用户认证依赖
- 权限控制系统
- 安全的 API 访问

## 🚦 快速开始

### 环境要求
- Python 3.8+
- pip 包管理器

### 安装依赖

```bash
# 克隆项目
git clone https://github.com/yourusername/fastapi-blog-basic.git
cd fastapi-blog-basic

# 安装依赖 (以 v7_jwt 为例)
cd versions/v7_jwt
pip install fastapi uvicorn sqlalchemy aiosqlite python-jose[cryptography] python-multipart email-validator
```

### 运行应用

```bash
# 启动开发服务器
uvicorn main:app --reload

# 访问应用
# API 文档: http://localhost:8000/docs
# 应用首页: http://localhost:8000
```

## 📋 API 接口

### 用户相关
- `POST /users/register` - 用户注册
- `POST /users/login` - 用户登录
- `GET /users/profile` - 获取用户信息
- `GET /users` - 用户列表

### 文章相关
- `POST /posts` - 创建文章
- `GET /posts` - 文章列表 (支持分页和搜索)
- `GET /posts/{id}` - 文章详情
- `PUT /posts/{id}` - 更新文章
- `DELETE /posts/{id}` - 删除文章
- `GET /users/{id}/posts` - 用户文章列表

### 系统相关
- `GET /` - 应用信息
- `GET /health` - 健康检查

## 🔧 配置说明

### JWT 配置 (v7_jwt)
```python
SECRET_KEY = "your-secret-key"  # 生产环境请使用强密钥
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
```

### 数据库配置
```python
DATABASE_URL = "sqlite:///./blog.db"  # SQLite 数据库
# 生产环境建议使用 PostgreSQL
```

## 🤝 贡献指南

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 开源协议

本项目采用 MIT 协议 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- [FastAPI](https://fastapi.tiangolo.com/) - 现代、快速的 Web 框架
- [SQLAlchemy](https://www.sqlalchemy.org/) - Python SQL 工具包
- [Pydantic](https://pydantic-docs.helpmanual.io/) - 数据验证库

## 📞 联系方式

如有问题或建议，欢迎通过以下方式联系：

- 提交 Issue
- 发起 Discussion
- 邮件联系

---

⭐ 如果这个项目对你有帮助，请给个 Star 支持一下！