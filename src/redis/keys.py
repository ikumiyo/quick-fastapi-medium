from src.core.config import settings


def build_key(*parts: str) -> str:
    """统一生成 Redis key。"""
    clean_parts = [part.strip(":") for part in parts if part]
    return ":".join([settings.REDIS_KEY_PREFIX, *clean_parts])
