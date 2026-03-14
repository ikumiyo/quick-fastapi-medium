from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from src.api.deps import AuthServiceDep, get_current_active_user
from src.models.user import User
from src.schemas.auth import RefreshTokenRequest, TokenResponse
from src.schemas.user import UserPublic

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: AuthServiceDep,
) -> TokenResponse:
    """用户名或邮箱登录。"""
    return service.login(account=form_data.username, password=form_data.password)


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(
    payload: RefreshTokenRequest,
    service: AuthServiceDep,
) -> TokenResponse:
    """刷新 access token。"""
    return service.refresh(refresh_token=payload.refresh_token)


@router.get("/me", response_model=UserPublic)
def me(current_user: Annotated[User, Depends(get_current_active_user)]) -> UserPublic:
    """获取当前登录用户。"""
    return current_user
