from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from src.api.deps import UserServiceDep, get_current_active_user, require_admin
from src.models.user import User
from src.schemas.user import UserCreate, UserPublic, UserUpdate

router = APIRouter()


@router.post("/", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def create_user(user_in: UserCreate, service: UserServiceDep) -> UserPublic:
    """注册用户。"""
    return service.create_user(user_in=user_in)


@router.get("/", response_model=list[UserPublic], dependencies=[Depends(require_admin)])
def list_users(
    *,
    skip: Annotated[int, Query(ge=0, description="分页起始偏移量")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="单页返回条数")] = 20,
    service: UserServiceDep,
) -> list[UserPublic]:
    """获取用户列表。"""
    return service.list_users(skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserPublic)
def get_user(
    user_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    service: UserServiceDep,
) -> UserPublic:
    """获取用户详情。"""
    service.ensure_self_or_admin(
        current_user=current_user,
        target_user_id=user_id,
        message="没有权限查看该用户",
    )
    return service.get_or_404(user_id=user_id)


@router.patch("/{user_id}", response_model=UserPublic)
def update_user(
    user_id: int,
    user_in: UserUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    service: UserServiceDep,
) -> UserPublic:
    """更新用户信息。"""
    service.ensure_self_or_admin(
        current_user=current_user,
        target_user_id=user_id,
        message="没有权限修改其他用户信息",
    )
    return service.update_user_profile(user_id=user_id, user_in=user_in)
