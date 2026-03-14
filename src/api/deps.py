from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session, sessionmaker

from redis import Redis
from src.core.exceptions import (
    AccountDisabledError,
    PermissionDeniedError,
    TokenInvalidError,
    TokenTypeError,
    UserNotFoundError,
)
from src.core.resources import AppResources, get_app_resources
from src.core.security import decode_token
from src.crud.file import file_crud
from src.crud.post import post_crud
from src.crud.user import user_crud
from src.models.user import User
from src.sdk.storage.base import BaseStorage
from src.services.admin import AdminService
from src.services.auth import AuthService
from src.services.file import FileService
from src.services.post import PostService
from src.services.task import TaskService
from src.services.user import UserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_session_factory(
    resources: Annotated[AppResources, Depends(get_app_resources)],
) -> sessionmaker:
    """获取共享数据库会话工厂。"""
    return resources.session_factory


def get_db_session(session_factory: Annotated[sessionmaker, Depends(get_session_factory)]):
    """为每个请求创建独立数据库会话。"""
    db = session_factory()
    try:
        yield db
    finally:
        db.close()


def get_redis(resources: Annotated[AppResources, Depends(get_app_resources)]) -> Redis | None:
    """获取共享 Redis 客户端。"""
    return resources.redis


def get_storage_backend(
    resources: Annotated[AppResources, Depends(get_app_resources)],
) -> BaseStorage:
    """获取共享存储后端。"""
    return resources.storage


DBSession = Annotated[Session, Depends(get_db_session)]
RedisClient = Annotated[Redis | None, Depends(get_redis)]
StorageBackend = Annotated[BaseStorage, Depends(get_storage_backend)]


def get_user_service(db: DBSession) -> UserService:
    """获取用户服务。"""
    return UserService(user_crud, db)


def get_post_service(db: DBSession) -> PostService:
    """获取文章服务。"""
    return PostService(post_crud, db)


def get_auth_service(
    user_service: Annotated[UserService, Depends(get_user_service)],
    redis_client: RedisClient,
) -> AuthService:
    """获取认证服务。"""
    return AuthService(user_service, redis_client)


def get_file_service(
    db: DBSession,
    storage: StorageBackend,
) -> FileService:
    """获取文件服务。"""
    return FileService(file_crud, db, storage)


def get_admin_service(db: DBSession) -> AdminService:
    """获取管理员服务。"""
    return AdminService(db)


def get_task_service() -> TaskService:
    """获取后台任务服务。"""
    return TaskService()


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
PostServiceDep = Annotated[PostService, Depends(get_post_service)]
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
FileServiceDep = Annotated[FileService, Depends(get_file_service)]
AdminServiceDep = Annotated[AdminService, Depends(get_admin_service)]
TaskServiceDep = Annotated[TaskService, Depends(get_task_service)]


def get_current_user(db: DBSession, token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    """获取当前登录用户。"""
    try:
        payload = decode_token(token)
    except JWTError as exc:
        raise TokenInvalidError("认证信息无效") from exc
    if payload.get("type") != "access":
        raise TokenTypeError("认证信息无效")
    user_id = payload.get("sub")
    if user_id is None:
        raise TokenInvalidError("认证信息无效")
    user = user_crud.get(db, int(user_id))
    if user is None:
        raise UserNotFoundError("用户不存在")
    return user


def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    """获取当前激活用户。"""
    if not current_user.is_active:
        raise AccountDisabledError("当前用户已被禁用")
    return current_user


def require_admin(current_user: Annotated[User, Depends(get_current_active_user)]) -> User:
    """要求管理员权限。"""
    if not current_user.is_admin:
        raise PermissionDeniedError("需要管理员权限")
    return current_user
