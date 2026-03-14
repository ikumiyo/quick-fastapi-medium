import json
from typing import Any

from redis.exceptions import RedisError

from redis import Redis
from src.core.exceptions import RedisOperationError
from src.redis.keys import build_key


def get_cache(client: Redis | None, namespace: str, identifier: str) -> dict[str, Any] | None:
    """读取 JSON 缓存。"""
    if client is None:
        return None
    try:
        value = client.get(build_key(namespace, identifier))
    except RedisError as exc:
        raise RedisOperationError("读取缓存失败") from exc
    if value is None:
        return None
    return json.loads(value)


def set_cache(
    client: Redis | None,
    namespace: str,
    identifier: str,
    payload: dict[str, Any],
    ttl: int = 300,
) -> None:
    """写入 JSON 缓存。"""
    if client is None:
        return
    try:
        client.set(
            build_key(namespace, identifier),
            json.dumps(payload, ensure_ascii=False),
            ex=ttl,
        )
    except RedisError as exc:
        raise RedisOperationError("写入缓存失败") from exc


def delete_cache(client: Redis | None, namespace: str, identifier: str) -> None:
    """删除缓存。"""
    if client is None:
        return
    try:
        client.delete(build_key(namespace, identifier))
    except RedisError as exc:
        raise RedisOperationError("删除缓存失败") from exc
