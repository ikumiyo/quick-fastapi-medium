from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from src.crud.base import CRUDBase
from src.models.post import Post


class CRUDPost(CRUDBase[Post]):
    """文章数据访问。"""

    def get_with_author(self, db: Session, *, item_id: int) -> Post | None:
        statement = select(Post).options(selectinload(Post.author)).where(Post.id == item_id)
        return db.scalar(statement)

    def get_published(self, db: Session, *, skip: int = 0, limit: int = 100) -> list[Post]:
        statement = select(Post).where(Post.published.is_(True)).offset(skip).limit(limit)
        return list(db.scalars(statement).all())

    def get_by_author(
        self,
        db: Session,
        *,
        author_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Post]:
        statement = select(Post).where(Post.author_id == author_id).offset(skip).limit(limit)
        return list(db.scalars(statement).all())

    def count_published(self, db: Session) -> int:
        return self.count(db, filters={"published": True})


post_crud = CRUDPost(Post)
