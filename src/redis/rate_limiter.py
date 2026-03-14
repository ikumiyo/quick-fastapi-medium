from redis.exceptions import RedisError

from redis import Redis
from src.core.exceptions import RedisOperationError
from src.redis.keys import build_key


def allow_request(
    client: Redis | None,
    identifier: str,
    resource: str,
    limit: int,
    window_seconds: int,
) -> bool:
    """简单计数限流。"""
    if client is None:
        return True
    key = build_key("rate_limit", resource, identifier)
    try:
        current = client.incr(key)
        if current == 1:
            client.expire(key, window_seconds)
    except RedisError as exc:
        raise RedisOperationError("执行限流检查失败") from exc
    return current <= limit
