import json
from typing import Any

import redis.asyncio as aioredis
from redis.asyncio import Redis
from redis.asyncio.connection import ConnectionPool
from redis.exceptions import RedisError

from src.core.config import Settings, settings
from src.core.exceptions import RedisOperationError


class RedisClient:
    """Redis 异步客户端封装。

    负责统一处理连接池、key 前缀、可空降级、JSON 序列化和异常包装。
    """

    def __init__(self, app_settings: Settings | None = None) -> None:
        self._settings = app_settings or settings
        self._pool: ConnectionPool | None = None
        self._redis: Redis | None = None

        if self._settings.REDIS_ENABLED:
            self._pool = ConnectionPool.from_url(
                self._settings.REDIS_URL,
                decode_responses=True,
            )
            self._redis = aioredis.Redis(connection_pool=self._pool)

    @property
    def enabled(self) -> bool:
        """Redis 是否启用。"""
        return self._redis is not None

    @property
    def raw(self) -> Redis | None:
        """底层 Redis 实例，用于本封装未覆盖的命令。"""
        return self._redis

    def make_key(self, *parts: str) -> str:
        """统一生成带项目前缀的 Redis key。"""
        clean_parts = [part.strip(":") for part in parts if part]
        return ":".join([self._settings.REDIS_KEY_PREFIX, *clean_parts])

    async def get(self, *key_parts: str) -> str | None:
        """读取字符串值，不存在或未启用时返回 None。"""
        if self._redis is None:
            return None
        try:
            return await self._redis.get(self.make_key(*key_parts))
        except RedisError as exc:
            raise RedisOperationError("读取键失败") from exc

    async def set(
        self,
        *key_parts: str,
        value: str,
        ttl: int | None = None,
        nx: bool = False,
    ) -> bool:
        """写入字符串值，未启用时返回 False。"""
        if self._redis is None:
            return False
        try:
            result = await self._redis.set(
                self.make_key(*key_parts),
                value,
                ex=ttl,
                nx=nx,
            )
        except RedisError as exc:
            raise RedisOperationError("写入键失败") from exc
        return bool(result)

    async def delete(self, *key_parts: str) -> int:
        """删除 key，返回删除数量；未启用时返回 0。"""
        if self._redis is None:
            return 0
        try:
            return await self._redis.delete(self.make_key(*key_parts))
        except RedisError as exc:
            raise RedisOperationError("删除键失败") from exc

    async def expire(self, *key_parts: str, ttl: int) -> bool:
        """设置 key 过期时间；未启用时返回 False。"""
        if self._redis is None:
            return False
        try:
            return bool(await self._redis.expire(self.make_key(*key_parts), ttl))
        except RedisError as exc:
            raise RedisOperationError("设置过期失败") from exc

    async def incr(self, *key_parts: str, amount: int = 1) -> int:
        """原子自增，未启用时返回 0。"""
        if self._redis is None:
            return 0
        try:
            return await self._redis.incrby(self.make_key(*key_parts), amount)
        except RedisError as exc:
            raise RedisOperationError("自增失败") from exc

    async def get_json(self, *key_parts: str) -> Any | None:
        """读取并反序列化 JSON，解析失败时返回 None。"""
        raw = await self.get(*key_parts)
        if raw is None:
            return None
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return None

    async def set_json(
        self,
        *key_parts: str,
        value: Any,
        ttl: int | None = None,
    ) -> bool:
        """序列化为 JSON 后写入。"""
        payload = json.dumps(value, ensure_ascii=False)
        return await self.set(*key_parts, value=payload, ttl=ttl)

    async def ping(self) -> bool:
        """健康检查，未启用或连接失败时返回 False。"""
        if self._redis is None:
            return False
        try:
            return bool(await self._redis.ping())
        except RedisError:
            return False

    async def close(self) -> None:
        """关闭 Redis 连接池。"""
        if self._redis is not None:
            await self._redis.aclose()
        if self._pool is not None:
            await self._pool.aclose()
