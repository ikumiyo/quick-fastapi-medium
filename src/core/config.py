import json
import os
from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

CURRENT_ENV = os.getenv("ENVIRONMENT", "development")


class Settings(BaseSettings):
    """应用配置。"""

    # 项目基本信息
    PROJECT_NAME: str = "Quick FastAPI Medium"  # 项目名称
    VERSION: str = "0.1.0"  # 版本号
    API_V1_STR: str = "/api/v1"  # API 路由前缀
    DEBUG: bool = True  # 是否开启调试模式
    ENVIRONMENT: str = CURRENT_ENV  # 当前环境（development/production 等）

    # 数据库配置
    DATABASE_URL: str = (
        "postgresql+psycopg://postgres:123456@localhost:5432/quick_fastapi_medium"
    )  # 数据库连接 URL
    DATABASE_ECHO: bool = False  # 是否输出 SQL 日志
    DATABASE_POOL_SIZE: int = 20  # 连接池大小
    DATABASE_MAX_OVERFLOW: int = 10  # 最大溢出连接数
    AUTO_CREATE_TABLES: bool = True  # 是否自动建表

    # Redis 配置
    REDIS_URL: str = "redis://localhost:6379/0"  # Redis 连接 URL
    REDIS_ENABLED: bool = False  # 是否启用 Redis
    REDIS_KEY_PREFIX: str = Field(
        default="quick-fastapi-medium",
        alias="REDIS_PREFIX",
    )  # Redis key 前缀

    # 安全相关
    SECRET_KEY: str = "change-me-in-production"  # JWT 密钥（生产环境请修改）
    ALGORITHM: str = "HS256"  # JWT 加密算法
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # 访问令牌有效分钟数
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7  # 刷新令牌有效天数
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]  # 允许跨域的来源

    # 日志相关
    LOG_LEVEL: str = "INFO"  # 日志等级
    LOG_FORMAT: str = "text"  # 日志格式（text/json）
    LOG_FILE_ENABLED: bool = False  # 是否启用文件日志
    LOG_FILE_PATH: str = "logs/app.log"  # 日志文件路径

    # 存储相关
    STORAGE_BACKEND: str = "local"  # 文件存储后端类型
    LOCAL_STORAGE_PATH: str = "storage"  # 本地存储路径

    # 管理员账户初始信息
    FIRST_SUPERUSER_EMAIL: str = "admin@example.com"  # 超级管理员邮箱
    FIRST_SUPERUSER_USERNAME: str = "admin"  # 超级管理员用户名
    FIRST_SUPERUSER_PASSWORD: str = "admin123456"  # 超级管理员密码

    # 监控/告警相关
    ENABLE_METRICS: bool = False  # 是否开启监控
    SENTRY_DSN: str = ""  # Sentry DSN 地址

    model_config = SettingsConfigDict(
        env_file=(".env", f".env.{CURRENT_ENV}"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_allowed_origins(cls, value: object) -> list[str]:
        """兼容 JSON 数组或逗号分隔字符串。"""
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            if value.startswith("["):
                return json.loads(value)
            return [item.strip() for item in value.split(",") if item.strip()]
        return ["http://localhost:3000"]

    @property
    def storage_path(self) -> Path:
        """本地存储目录。"""
        return Path(self.LOCAL_STORAGE_PATH)

    @property
    def log_file_path(self) -> Path:
        """日志文件路径。"""
        return Path(self.LOG_FILE_PATH)


@lru_cache
def get_settings() -> Settings:
    """获取单例配置对象。"""
    return Settings()


settings = get_settings()
