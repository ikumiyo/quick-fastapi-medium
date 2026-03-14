from jose import JWTError

from redis import Redis
from src.core.config import settings
from src.core.exceptions import (
    AccountDisabledError,
    InvalidCredentialsError,
    RefreshTokenRevokedError,
    TokenInvalidError,
    TokenSubjectMissingError,
    TokenTypeError,
)
from src.core.security import create_access_token, create_refresh_token, decode_token
from src.redis.session import get_refresh_token, revoke_refresh_token, store_refresh_token
from src.schemas.auth import TokenResponse
from src.services.user import UserService


class AuthService:
    """认证流程编排。"""

    def __init__(self, user_service: UserService, redis_client: Redis | None) -> None:
        self.user_service = user_service
        self.redis_client = redis_client

    def login(
        self,
        *,
        account: str,
        password: str,
    ) -> TokenResponse:
        user = self.user_service.authenticate(account=account, password=password)
        if user is None:
            raise InvalidCredentialsError("用户名或密码错误")
        if not user.is_active:
            raise AccountDisabledError("当前用户已被禁用")
        refresh_token = create_refresh_token(str(user.id))
        store_refresh_token(
            self.redis_client,
            user.id,
            refresh_token,
            settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        )
        return TokenResponse(
            access_token=create_access_token(str(user.id)),
            refresh_token=refresh_token,
        )

    def refresh(
        self,
        *,
        refresh_token: str,
    ) -> TokenResponse:
        try:
            payload = decode_token(refresh_token)
        except JWTError as exc:
            raise TokenInvalidError("刷新令牌无效") from exc
        if payload.get("type") != "refresh":
            raise TokenTypeError("令牌类型错误")

        user_id = payload.get("sub")
        if user_id is None:
            raise TokenSubjectMissingError("令牌主体缺失")
        user_id_int = int(user_id)
        user = self.user_service.get_or_404(user_id=user_id_int)
        if self.redis_client is not None:
            stored_token = get_refresh_token(self.redis_client, user_id_int)
            if stored_token is not None and stored_token != refresh_token:
                raise RefreshTokenRevokedError("刷新令牌已失效")
        new_refresh_token = create_refresh_token(str(user.id))
        revoke_refresh_token(self.redis_client, user.id)
        store_refresh_token(
            self.redis_client,
            user.id,
            new_refresh_token,
            settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        )
        return TokenResponse(
            access_token=create_access_token(str(user.id)),
            refresh_token=new_refresh_token,
        )
