from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from src.core.config import settings
from src.models.base import Base


def build_engine(database_url: str | None = None) -> Engine:
    """根据连接串构建数据库引擎。"""
    url = database_url or settings.DATABASE_URL
    connect_args: dict[str, object] = {}
    engine_kwargs: dict[str, object] = {"future": True}

    if url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    else:
        engine_kwargs["pool_size"] = settings.DATABASE_POOL_SIZE
        engine_kwargs["max_overflow"] = settings.DATABASE_MAX_OVERFLOW
        engine_kwargs["pool_pre_ping"] = True
    engine_kwargs["echo"] = settings.DATABASE_ECHO

    return create_engine(url, connect_args=connect_args, **engine_kwargs)


def build_session_factory(bind: Engine) -> sessionmaker:
    """根据引擎构建会话工厂。"""
    return sessionmaker(bind=bind, autocommit=False, autoflush=False, expire_on_commit=False)


def init_db(bind: Engine) -> None:
    """初始化数据库元数据。"""
    import src.models  # noqa: F401

    Base.metadata.create_all(bind=bind)
