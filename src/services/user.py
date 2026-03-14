from src.core.exceptions import (
    EmailAlreadyExistsError,
    PermissionDeniedError,
    UsernameAlreadyExistsError,
    UserNotFoundError,
)
from src.core.security import get_password_hash, verify_password
from src.crud.user import CRUDUser
from src.models.user import User
from src.schemas.user import UserCreate, UserUpdate
from src.services.base import BaseService


class UserService(BaseService[CRUDUser]):
    """用户业务逻辑。"""

    def authenticate(self, *, account: str, password: str) -> User | None:
        user = self.crud.get_by_account(self.db, account=account)
        if user is None or not verify_password(password, user.hashed_password):
            return None
        return user

    def create_user(self, *, user_in: UserCreate, is_admin: bool = False) -> User:
        if self.crud.email_exists(self.db, email=user_in.email):
            raise EmailAlreadyExistsError("邮箱已被注册")
        if self.crud.username_exists(self.db, username=user_in.username):
            raise UsernameAlreadyExistsError("用户名已被使用")
        return self.crud.create(
            self.db,
            obj_in={
                "email": user_in.email,
                "username": user_in.username,
                "full_name": user_in.full_name,
                "hashed_password": get_password_hash(user_in.password),
                "is_active": True,
                "is_admin": is_admin,
            },
        )

    def get_or_404(self, *, user_id: int) -> User:
        user = self.crud.get(self.db, user_id)
        if user is None:
            raise UserNotFoundError("用户不存在")
        return user

    def list_users(self, *, skip: int = 0, limit: int = 20) -> list[User]:
        return self.crud.get_multi(self.db, skip=skip, limit=limit)

    def ensure_self_or_admin(
        self,
        *,
        current_user: User,
        target_user_id: int,
        message: str,
    ) -> None:
        if current_user.id != target_user_id and not current_user.is_admin:
            raise PermissionDeniedError(message)

    def update_user_profile(self, *, user_id: int, user_in: UserUpdate) -> User:
        user = self.get_or_404(user_id=user_id)
        if user_in.email and user_in.email != user.email:
            existing_user = self.crud.get_by_email(self.db, email=user_in.email)
            if existing_user is not None:
                raise EmailAlreadyExistsError("邮箱已被使用")
        if user_in.username and user_in.username != user.username:
            existing_user = self.crud.get_by_username(self.db, username=user_in.username)
            if existing_user is not None:
                raise UsernameAlreadyExistsError("用户名已被使用")

        update_data = user_in.model_dump(exclude_unset=True)
        password = update_data.pop("password", None)
        if password:
            update_data["hashed_password"] = get_password_hash(password)
        return self.crud.update(self.db, db_obj=user, obj_in=update_data)
