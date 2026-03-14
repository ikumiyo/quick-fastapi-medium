import logging

from src.core.database import init_db
from src.core.logging import configure_logging
from src.core.resources import (
    AppResources,
    close_app_resources,
    create_app_resources,
    set_app_resources,
)

logger = logging.getLogger(__name__)


def on_startup(app) -> AppResources:
    """应用启动时执行。"""
    # 配置日志系统
    configure_logging()
    # 创建应用资源（数据库连接、Redis 等）
    resources = create_app_resources()
    # 绑定应用资源到 app 实例
    set_app_resources(app, resources)
    # 如果配置允许，则自动建表（仅用于开发环境，生产建议关闭）
    if resources.settings.AUTO_CREATE_TABLES:
        init_db(resources.engine)
    logger.info("application_started")  # 记录启动日志
    return resources


def on_shutdown(app) -> None:
    """应用关闭时执行。"""
    # 尝试从 app 中获取资源
    resources = getattr(app.state, "resources", None)
    # 如果资源存在，则关闭连接和资源
    if resources is not None:
        close_app_resources(resources)
    logger.info("application_stopped")  # 记录关闭日志
