"""创建默认管理员账号。"""

from src.core.config import settings
from src.core.database import build_engine, build_session_factory
from src.crud.user import user_crud
from src.schemas.user import UserCreate
from src.services.user import UserService


def main() -> None:
    """根据环境变量创建管理员。"""
    engine = build_engine()
    session_factory = build_session_factory(engine)
    session = session_factory()
    try:
        user_service = UserService(user_crud, session)

        existing = user_service.crud.get_by_email(
            session,
            email=settings.FIRST_SUPERUSER_EMAIL,
        )
        if existing:
            print("ℹ️ 管理员已存在，跳过创建")
            return

        user_service.create_user(
            user_in=UserCreate(
                email=settings.FIRST_SUPERUSER_EMAIL,
                username=settings.FIRST_SUPERUSER_USERNAME,
                password=settings.FIRST_SUPERUSER_PASSWORD,
            ),
            is_admin=True,
        )
        print("✅ 管理员创建完成")
    finally:
        session.close()
        engine.dispose()


if __name__ == "__main__":
    main()
