from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from src.api.deps import PostServiceDep, get_current_active_user
from src.models.user import User
from src.schemas.post import PostCreate, PostDetail, PostPublic, PostUpdate

router = APIRouter()


@router.post("/", response_model=PostPublic, status_code=status.HTTP_201_CREATED)
def create_post(
    post_in: PostCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    service: PostServiceDep,
) -> PostPublic:
    """创建文章。"""
    return service.create_post(current_user=current_user, post_in=post_in)


@router.get("/", response_model=list[PostPublic])
def list_posts(
    *,
    skip: Annotated[int, Query(ge=0, description="分页起始偏移量")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="单页返回条数")] = 20,
    published_only: bool = Query(default=False),
    service: PostServiceDep,
) -> list[PostPublic]:
    """文章列表。"""
    return service.list_posts(
        skip=skip,
        limit=limit,
        published_only=published_only,
    )


@router.get("/{post_id}", response_model=PostDetail)
def get_post(post_id: int, service: PostServiceDep) -> PostDetail:
    """文章详情。"""
    return service.get_or_404(post_id=post_id)


@router.patch("/{post_id}", response_model=PostPublic)
def update_post(
    post_id: int,
    post_in: PostUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    service: PostServiceDep,
) -> PostPublic:
    """更新文章。"""
    return service.update_post(post_id=post_id, current_user=current_user, post_in=post_in)
