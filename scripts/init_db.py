"""初始化数据库并创建基础数据。"""

from src.core.database import build_engine, build_session_factory, init_db
from src.models import (
    base,  # noqa: F401
    file,  # noqa: F401
    post,  # noqa: F401
    user,  # noqa: F401
)


def main() -> None:
    """创建所有表。"""
    engine = build_engine()
    session_factory = build_session_factory(engine)
    session = session_factory()
    try:
        init_db(engine)
        print("✅ 数据库初始化完成")
    finally:
        session.close()
        engine.dispose()


if __name__ == "__main__":
    main()
