from dataclasses import dataclass

from fastapi import FastAPI, Request
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from src.core.config import Settings, settings
from src.infra.db.database import build_engine, build_session_factory
from src.infra.redis.client import RedisClient
from src.infra.storage import build_storage_backend
from src.infra.storage.base import BaseStorage


@dataclass(slots=True)
class AppResources:
    """应用共享资源容器。"""

    settings: Settings
    engine: Engine
    session_factory: sessionmaker
    storage: BaseStorage
    redis: RedisClient


def create_app_resources(app_settings: Settings | None = None) -> AppResources:
    """创建应用共享资源。"""
    current_settings = app_settings or settings
    engine = build_engine(current_settings.DATABASE_URL)
    session_factory = build_session_factory(engine)
    storage = build_storage_backend(current_settings)
    redis_client = RedisClient(current_settings)

    return AppResources(
        settings=current_settings,
        engine=engine,
        session_factory=session_factory,
        storage=storage,
        redis=redis_client,
    )


async def close_app_resources(resources: AppResources) -> None:
    """关闭应用共享资源。"""
    await resources.redis.close()
    resources.engine.dispose()


def set_app_resources(app: FastAPI, resources: AppResources) -> None:
    """将共享资源挂载到应用实例。"""
    app.state.resources = resources


def get_app_resources_from_app(app: FastAPI) -> AppResources:
    """从应用实例读取共享资源。"""
    resources = getattr(app.state, "resources", None)
    if resources is None:
        raise RuntimeError("应用共享资源尚未初始化，请确认 lifespan / startup 已正确执行")
    return resources


def get_app_resources(request: Request) -> AppResources:
    """从请求上下文读取共享资源。"""
    return get_app_resources_from_app(request.app)
