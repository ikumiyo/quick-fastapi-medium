from fastapi import FastAPI
from redis.exceptions import RedisError

from redis import Redis
from src.core.exceptions import RedisOperationError
from src.core.resources import get_app_resources_from_app


def get_redis_client(app: FastAPI) -> Redis | None:
    """获取 Redis 客户端。"""
    return get_app_resources_from_app(app).redis


def ping_redis(client: Redis | None) -> bool:
    """检查 Redis 是否可用。"""
    if client is None:
        return False
    try:
        return bool(client.ping())
    except RedisError as exc:
        raise RedisOperationError("Redis 健康检查失败") from exc
