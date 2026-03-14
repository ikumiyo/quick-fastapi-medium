from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.api.deps import get_db_session
from src.core.config import settings
from src.crud.user import user_crud
from src.main import app
from src.models.base import Base
from src.schemas.user import UserCreate
from src.services.user import UserService


@pytest.fixture()
def db_session(tmp_path: Path) -> Generator[Session, None, None]:
    """创建独立测试数据库会话。"""
    database_path = tmp_path / "test.db"
    engine = create_engine(f"sqlite:///{database_path}", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture()
def client(db_session: Session, tmp_path: Path) -> Generator[TestClient, None, None]:
    """创建测试客户端。"""
    original_auto_create_tables = settings.AUTO_CREATE_TABLES
    original_storage_path = settings.LOCAL_STORAGE_PATH
    settings.AUTO_CREATE_TABLES = False
    settings.LOCAL_STORAGE_PATH = str(tmp_path / "storage")

    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db_session] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    settings.AUTO_CREATE_TABLES = original_auto_create_tables
    settings.LOCAL_STORAGE_PATH = original_storage_path


@pytest.fixture()
def normal_user(db_session: Session):
    """创建普通用户。"""
    user_service = UserService(user_crud, db_session)
    return user_service.create_user(
        user_in=UserCreate(
            email="user@example.com",
            username="normal-user",
            full_name="Normal User",
            password="Password123",
        ),
    )


@pytest.fixture()
def admin_user(db_session: Session):
    """创建管理员用户。"""
    user_service = UserService(user_crud, db_session)
    return user_service.create_user(
        user_in=UserCreate(
            email="admin@example.com",
            username="admin-user",
            full_name="Admin User",
            password="Password123",
        ),
        is_admin=True,
    )


def _login(client: TestClient, account: str, password: str) -> str:
    response = client.post(
        "/api/v1/auth/login",
        data={"username": account, "password": password},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture()
def user_token(client: TestClient, normal_user) -> str:
    """获取普通用户 token。"""
    return _login(client, normal_user.email, "Password123")


@pytest.fixture()
def admin_token(client: TestClient, admin_user) -> str:
    """获取管理员 token。"""
    return _login(client, admin_user.username, "Password123")
