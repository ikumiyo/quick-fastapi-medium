from src.core.exceptions import PermissionDeniedError, PostNotFoundError
from src.crud.post import CRUDPost
from src.models.post import Post
from src.models.user import User
from src.schemas.post import PostCreate, PostUpdate
from src.services.base import BaseService


class PostService(BaseService[CRUDPost]):
    """文章业务逻辑。"""

    def create_post(self, *, current_user: User, post_in: PostCreate) -> Post:
        return self.crud.create(
            self.db,
            obj_in={
                "title": post_in.title,
                "summary": post_in.summary,
                "content": post_in.content,
                "published": post_in.published,
                "author_id": current_user.id,
            },
        )

    def get_or_404(self, *, post_id: int) -> Post:
        post = self.crud.get_with_author(self.db, item_id=post_id)
        if post is None:
            raise PostNotFoundError("文章不存在")
        return post

    def update_post(
        self,
        *,
        post_id: int,
        current_user: User,
        post_in: PostUpdate,
    ) -> Post:
        post = self.get_or_404(post_id=post_id)
        if post.author_id != current_user.id and not current_user.is_admin:
            raise PermissionDeniedError("没有权限修改该文章")
        return self.crud.update(self.db, db_obj=post, obj_in=post_in)

    def list_posts(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        published_only: bool = False,
    ) -> list[Post]:
        if published_only:
            return self.crud.get_published(self.db, skip=skip, limit=limit)
        return self.crud.get_multi(self.db, skip=skip, limit=limit)
