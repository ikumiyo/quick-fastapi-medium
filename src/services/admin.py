from sqlalchemy.orm import Session

from src.crud.file import file_crud
from src.crud.post import post_crud
from src.crud.user import user_crud
from src.models.user import User
from src.schemas.admin import AdminDashboardResponse, AdminDashboardStats


class AdminService:
    """管理员业务逻辑。"""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_dashboard(self, *, current_user: User) -> AdminDashboardResponse:
        return AdminDashboardResponse(
            message=f"欢迎你，管理员 {current_user.username}",
            stats=AdminDashboardStats(
                users=user_crud.count(self.db),
                posts=post_crud.count(self.db),
                published_posts=post_crud.count_published(self.db),
                files=file_crud.count(self.db),
            ),
        )
