from src.schemas.base import TimestampSchema


class FilePublic(TimestampSchema):
    """文件响应。"""

    original_name: str
    stored_name: str
    content_type: str | None
    size: int
    url: str
    owner_id: int
