from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ORMSchema(BaseModel):
    """开启 ORM 映射支持。"""

    model_config = ConfigDict(from_attributes=True)


class TimestampSchema(ORMSchema):
    """包含时间字段的响应模型。"""

    id: int
    created_at: datetime
    updated_at: datetime


class MessageSchema(BaseModel):
    """通用消息响应。"""

    message: str
