from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, IDMixin, TimestampMixin

if TYPE_CHECKING:
    from src.models.user import User


class Post(Base, IDMixin, TimestampMixin):
    """文章模型。"""

    __tablename__ = "posts"

    title: Mapped[str] = mapped_column(String(200), index=True)
    summary: Mapped[str | None] = mapped_column(String(300), nullable=True)
    content: Mapped[str] = mapped_column(Text)
    published: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)

    author: Mapped[User] = relationship(back_populates="posts")
