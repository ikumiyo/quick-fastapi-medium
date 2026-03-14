from pydantic import BaseModel


class TokenResponse(BaseModel):
    """令牌响应。"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    """刷新令牌请求。"""

    refresh_token: str
