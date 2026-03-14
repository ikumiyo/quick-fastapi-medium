from collections.abc import Iterator
from contextlib import contextmanager

from redis.exceptions import RedisError

from redis import Redis
from src.core.exceptions import RedisOperationError
from src.redis.keys import build_key


@contextmanager
def distributed_lock(client: Redis | None, name: str, timeout: int = 10) -> Iterator[bool]:
    """分布式锁封装。"""
    if client is None:
        yield True
        return
    try:
        lock = client.lock(build_key("lock", name), timeout=timeout)
        acquired = lock.acquire(blocking=False)
    except RedisError as exc:
        raise RedisOperationError("获取分布式锁失败") from exc
    try:
        yield acquired
    finally:
        if acquired:
            try:
                lock.release()
            except RedisError as exc:
                raise RedisOperationError("释放分布式锁失败") from exc
