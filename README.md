<div align="center">

# Quick FastAPI Medium

**生产就绪的 FastAPI 中型项目模板**

适用于 3 ~ 8 人团队的后端骨架，开箱即用，分层清晰，易于扩展。

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-D71F00?style=flat-square)](https://www.sqlalchemy.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-336791?style=flat-square&logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![Redis](https://img.shields.io/badge/Redis-7+-DC382D?style=flat-square&logo=redis&logoColor=white)](https://redis.io)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

[快速开始](#快速开始) · [项目结构](#项目结构) · [架构设计](#架构设计) · [部署指南](#部署) · [文档](#文档)

</div>

---

## 简介

`quick-fastapi-medium` 是一个面向中型后端项目的 FastAPI 模板，基于严格的分层架构设计，内置认证、数据库迁移、Redis、文件上传、异步任务、结构化日志、统一异常处理等常见能力，让你专注于业务逻辑，而不是重复搭建基础设施。

### 适合谁使用

- 需要快速启动一个有一定规模的 FastAPI 后端项目
- 团队规模在 3 ~ 8 人，需要清晰的代码分层约定
- 希望从第一天起就有可测试、可扩展的项目骨架

---

## 核心特性

| 特性 | 说明 |
|------|------|
| **分层架构** | `API → Service → CRUD → Model`，职责边界清晰 |
| **JWT 认证** | Access Token + Refresh Token，支持管理员鉴权 |
| **数据库** | PostgreSQL + SQLAlchemy 2.0 + Alembic 迁移 |
| **Redis** | 缓存、会话、分布式锁、限流，开箱即用 |
| **结构化日志** | JSON 格式日志，内置 `request_id` 追踪 |
| **统一异常** | `AppError` 异常体系，全局处理器，稳定错误协议 |
| **文件上传** | 本地存储后端示例，可扩展为 S3/OSS |
| **异步任务** | FastAPI `BackgroundTasks` 示例，可扩展为 Celery |
| **API 版本化** | 统一 `/api/v1` 前缀，便于后续版本迭代 |
| **自动文档** | Swagger UI + ReDoc，零配置 |
| **测试骨架** | 单元测试 + 集成测试目录结构，pytest 配置完善 |
| **容器化** | Docker / Docker Compose / Kubernetes 配置齐全 |

---

## 快速开始

### 环境要求

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) 包管理器
- PostgreSQL 14+
- Redis 7+（可选，默认关闭）

### 1. 克隆项目

```bash
git clone https://github.com/ikumiyo/quick-fastapi-medium.git
cd quick-fastapi-medium
```

### 2. 配置环境变量

```bash
cp .env.example .env
```

按需修改 `.env` 中的数据库连接、密钥等配置（详见[配置说明](#配置说明)）。

### 3. 安装依赖

```bash
uv sync
```

### 4. 初始化数据库

```bash
uv run alembic upgrade head
uv run python scripts/init_db.py
uv run python scripts/create_admin.py
```

### 5. 启动服务

```bash
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

服务启动后访问：

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc
- **健康检查**: http://127.0.0.1:8000/health

---

## 使用 Docker 启动（推荐）

无需本地安装 PostgreSQL，一条命令启动完整开发环境：

```bash
docker compose -f docker/docker-compose.yml up --build
```

> Docker Compose 会自动启动 Redis，API 容器连接宿主机 PostgreSQL。详见 [Docker 部署说明](docker/README.md)。

---

## 项目结构

```text
quick-fastapi-medium/
├── src/
│   ├── main.py              # 应用装配入口
│   ├── api/
│   │   ├── deps.py          # 依赖注入工厂（统一出口）
│   │   └── v1/
│   │       ├── api.py       # 路由聚合
│   │       └── routers/     # 按业务域拆分的路由
│   │           ├── auth.py
│   │           ├── users.py
│   │           ├── posts.py
│   │           ├── files.py
│   │           ├── tasks.py
│   │           └── admin.py
│   ├── core/
│   │   ├── config.py        # 全局配置（pydantic-settings）
│   │   ├── database.py      # 数据库引擎构建
│   │   ├── resources.py     # 共享资源管理（AppResources）
│   │   ├── events.py        # 生命周期钩子
│   │   ├── exceptions.py    # 异常体系与全局处理器
│   │   ├── logging.py       # 结构化日志配置
│   │   └── security.py      # JWT / 密码哈希
│   ├── services/            # 业务逻辑层
│   ├── crud/                # 数据访问层
│   ├── models/              # ORM 模型
│   ├── schemas/             # Pydantic 请求/响应 schema
│   ├── middleware/          # 请求 ID、耗时统计
│   ├── redis/               # Redis 缓存、锁、限流封装
│   ├── sdk/                 # 外部服务接入预留
│   └── tasks/               # 异步任务预留
├── tests/
│   ├── unit/                # 单元测试
│   └── integration/         # 集成测试
├── alembic/                 # 数据库迁移脚本
├── scripts/                 # 初始化脚本
├── docker/                  # Docker 配置
├── k8s/                     # Kubernetes 配置
└── docs/                    # 项目文档
```

---

## 架构设计

```
HTTP Request
     ↓
┌─────────────────────────────────────┐
│  API Layer  (src/api/)              │  路由、参数校验、HTTP 语义、依赖注入
└─────────────────────────────────────┘
     ↓
┌─────────────────────────────────────┐
│  Service Layer  (src/services/)     │  业务规则、权限判断、流程编排
└─────────────────────────────────────┘
     ↓
┌─────────────────────────────────────┐
│  CRUD Layer  (src/crud/)            │  数据访问、ORM 封装、写入提交
└─────────────────────────────────────┘
     ↓
┌─────────────────────────────────────┐
│  Model Layer  (src/models/)         │  ORM 模型、表结构定义
└─────────────────────────────────────┘
     ↓
  PostgreSQL
```

每一层职责单一，依赖方向严格单向，便于独立测试和替换。

---

## 内置业务模块

| 模块 | 路由前缀 | 说明 |
|------|----------|------|
| `auth` | `/api/v1/auth` | 登录、刷新令牌、获取当前用户 |
| `users` | `/api/v1/users` | 用户注册、查询、更新 |
| `posts` | `/api/v1/posts` | 文章创建、列表、发布 |
| `files` | `/api/v1/files` | 文件上传示例 |
| `tasks` | `/api/v1/tasks` | 后台任务示例 |
| `admin` | `/api/v1/admin` | 管理员受保护接口示例 |

---

## 配置说明

所有配置通过 `.env` 文件驱动，支持按环境覆盖（`.env.development`、`.env.production`）。

```env
# 应用
PROJECT_NAME=Quick FastAPI Medium
DEBUG=true
ENVIRONMENT=development

# 数据库
DATABASE_URL=postgresql+psycopg://postgres:123456@localhost:5432/quick_fastapi_medium

# Redis（可选）
REDIS_ENABLED=false
REDIS_URL=redis://localhost:6379/0

# 安全（生产环境务必修改）
SECRET_KEY=change-me-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# 跨域
ALLOWED_ORIGINS=["http://localhost:3000"]

# 日志
LOG_LEVEL=INFO
LOG_FORMAT=text
```

完整配置项见 [`src/core/config.py`](src/core/config.py)。

---

## 测试

```bash
# 运行全部测试
uv run pytest

# 带覆盖率报告
uv run pytest --cov=src --cov-report=term-missing
```

---

## 代码质量

```bash
# 检查
uv run ruff check .

# 格式化
uv run ruff format .
```

---

## 部署

### Docker Compose（开发）

```bash
docker compose -f docker/docker-compose.yml up --build
```

### Docker Compose（生产）

```bash
docker compose -f docker/docker-compose.prod.yml up --build -d
```

### Kubernetes

```bash
kubectl apply -k k8s/overlays/dev
```

详细部署说明见 [docs/deployment.md](docs/deployment.md) 和 [docker/README.md](docker/README.md)。

---

## 文档

| 文档 | 说明 |
|------|------|
| [架构说明](docs/architecture.md) | 分层设计与数据流 |
| [API 说明](docs/api.md) | 接口约定与示例 |
| [部署说明](docs/deployment.md) | 生产部署指南 |
| [FastAPI 入口与 lifespan](docs/01_fastapi_main_lifespan.md) | main.py 设计讲解 |
| [core/resources.py 设计](docs/02_core_resources_design.md) | 共享资源管理 |
| [日志与异常设计](docs/03_logging_and_exceptions_design.md) | 结构化日志与异常体系 |
| [异常系统设计](docs/06_exception_system_design.md) | 异常重构后的完整设计 |
| [core/security.py 设计](docs/08_core_security_design.md) | JWT 与密码安全 |
| [Docker 部署详解](docker/README.md) | 容器化部署完整说明 |

---

## 后续扩展建议

- 按业务模块继续扩展 `services/` 与 `crud/`
- 启用 Celery + Redis 实现生产级异步任务
- 扩展存储后端支持 S3 / 阿里云 OSS
- 接入 Sentry 错误监控
- 接入 Prometheus + Grafana 指标监控
- 配置 CI/CD 流水线（GitHub Actions / GitLab CI）
- 扩展 PostgreSQL 索引、分区和读写分离策略

---

## 贡献

欢迎提交 Issue 和 Pull Request。

1. Fork 本仓库
2. 创建你的特性分支：`git checkout -b feature/your-feature`
3. 提交变更：`git commit -m 'feat: add your feature'`
4. 推送分支：`git push origin feature/your-feature`
5. 发起 Pull Request

---

## License

[MIT](LICENSE)
