from pydantic import BaseModel, EmailStr, Field

from src.schemas.base import TimestampSchema


class UserBase(BaseModel):
    """用户基础字段。"""

    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    full_name: str | None = Field(default=None, max_length=100)


class UserCreate(UserBase):
    """创建用户请求。"""

    password: str = Field(min_length=8, max_length=128)


class UserUpdate(BaseModel):
    """更新用户请求。"""

    email: EmailStr | None = None
    username: str | None = Field(default=None, min_length=3, max_length=50)
    full_name: str | None = Field(default=None, max_length=100)
    password: str | None = Field(default=None, min_length=8, max_length=128)


class UserPublic(TimestampSchema, UserBase):
    """用户公开响应。"""

    is_active: bool
    is_admin: bool
