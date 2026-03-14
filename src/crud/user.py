from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from src.crud.base import CRUDBase
from src.models.user import User


class CRUDUser(CRUDBase[User]):
    """用户数据访问。"""

    def get_by_email(self, db: Session, *, email: str) -> User | None:
        return db.scalar(select(User).where(User.email == email))

    def get_by_username(self, db: Session, *, username: str) -> User | None:
        return db.scalar(select(User).where(User.username == username))

    def get_by_account(self, db: Session, *, account: str) -> User | None:
        statement = select(User).where(or_(User.email == account, User.username == account))
        return db.scalar(statement)

    def email_exists(self, db: Session, *, email: str) -> bool:
        return self.get_by_email(db, email=email) is not None

    def username_exists(self, db: Session, *, username: str) -> bool:
        return self.get_by_username(db, username=username) is not None


user_crud = CRUDUser(User)
