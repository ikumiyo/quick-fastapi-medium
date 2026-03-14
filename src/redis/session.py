from redis.exceptions import RedisError

from redis import Redis
from src.core.exceptions import RedisOperationError
from src.redis.keys import build_key


def store_refresh_token(
    client: Redis | None,
    user_id: int,
    refresh_token: str,
    ttl_seconds: int,
) -> None:
    """保存 refresh token。"""
    if client is None:
        return
    try:
        client.set(build_key("auth", "refresh", str(user_id)), refresh_token, ex=ttl_seconds)
    except RedisError as exc:
        raise RedisOperationError("保存刷新令牌失败") from exc


def revoke_refresh_token(client: Redis | None, user_id: int) -> None:
    """删除 refresh token。"""
    if client is None:
        return
    try:
        client.delete(build_key("auth", "refresh", str(user_id)))
    except RedisError as exc:
        raise RedisOperationError("删除刷新令牌失败") from exc


def get_refresh_token(client: Redis | None, user_id: int) -> str | None:
    """读取 refresh token。"""
    if client is None:
        return None
    try:
        return client.get(build_key("auth", "refresh", str(user_id)))
    except RedisError as exc:
        raise RedisOperationError("读取刷新令牌失败") from exc
