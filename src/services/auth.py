from jose import JWTError

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
from src.redis.client import RedisClient
from src.schemas.auth import TokenResponse
from src.services.user import UserService


class AuthService:
    """认证流程编排。"""

    def __init__(self, user_service: UserService, redis_client: RedisClient) -> None:
        self.user_service = user_service
        self.redis_client = redis_client

    async def login(
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
        await self.redis_client.set(
            "auth",
            "refresh",
            str(user.id),
            value=refresh_token,
            ttl=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        )
        return TokenResponse(
            access_token=create_access_token(str(user.id)),
            refresh_token=refresh_token,
        )

    async def refresh(
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
        stored_token = await self.redis_client.get("auth", "refresh", str(user_id_int))
        if stored_token is not None and stored_token != refresh_token:
            raise RefreshTokenRevokedError("刷新令牌已失效")
        new_refresh_token = create_refresh_token(str(user.id))
        await self.redis_client.delete("auth", "refresh", str(user.id))
        await self.redis_client.set(
            "auth",
            "refresh",
            str(user.id),
            value=new_refresh_token,
            ttl=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        )
        return TokenResponse(
            access_token=create_access_token(str(user.id)),
            refresh_token=new_refresh_token,
        )
