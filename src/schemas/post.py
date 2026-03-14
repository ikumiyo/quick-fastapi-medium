from pydantic import BaseModel, Field

from src.schemas.base import ORMSchema, TimestampSchema
from src.schemas.user import UserPublic


class PostBase(BaseModel):
    """文章基础字段。"""

    title: str = Field(min_length=1, max_length=200)
    summary: str | None = Field(default=None, max_length=300)
    content: str = Field(min_length=1)
    published: bool = False


class PostCreate(PostBase):
    """创建文章请求。"""


class PostUpdate(BaseModel):
    """更新文章请求。"""

    title: str | None = Field(default=None, min_length=1, max_length=200)
    summary: str | None = Field(default=None, max_length=300)
    content: str | None = Field(default=None, min_length=1)
    published: bool | None = None


class PostPublic(TimestampSchema, PostBase):
    """文章响应。"""

    author_id: int


class PostDetail(PostPublic):
    """文章详情响应。"""

    author: UserPublic | None = None


class PostSummary(ORMSchema):
    """文章统计摘要。"""

    total: int
    published: int
