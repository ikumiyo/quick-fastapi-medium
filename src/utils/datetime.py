from datetime import UTC, datetime


def utcnow() -> datetime:
    """获取当前 UTC 时间。"""
    return datetime.now(UTC)
