import base64
import hashlib
import hmac
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt

from src.core.config import settings

PBKDF2_ALGORITHM = "pbkdf2_sha256"
PBKDF2_ITERATIONS = 600_000


def _b64encode(raw: bytes) -> str:
    """编码字节串。"""
    return base64.b64encode(raw).decode("utf-8")


def _b64decode(raw: str) -> bytes:
    """解码字节串。"""
    return base64.b64decode(raw.encode("utf-8"))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """校验密码。"""
    try:
        algorithm, iterations, salt, digest = hashed_password.split("$", maxsplit=3)
    except ValueError:
        return False
    if algorithm != PBKDF2_ALGORITHM:
        return False
    candidate = hashlib.pbkdf2_hmac(
        "sha256",
        plain_password.encode("utf-8"),
        _b64decode(salt),
        int(iterations),
    )
    return hmac.compare_digest(_b64encode(candidate), digest)


def get_password_hash(password: str) -> str:
    """生成密码哈希。"""
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PBKDF2_ITERATIONS,
    )
    return f"{PBKDF2_ALGORITHM}${PBKDF2_ITERATIONS}${_b64encode(salt)}${_b64encode(digest)}"


def _build_token(subject: str, token_type: str, expires_delta: timedelta) -> str:
    """生成指定类型的 JWT。"""
    expire = datetime.now(UTC) + expires_delta
    payload: dict[str, Any] = {"sub": subject, "exp": expire, "type": token_type}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    """生成访问令牌。"""
    return _build_token(
        subject,
        "access",
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def create_refresh_token(subject: str, expires_delta: timedelta | None = None) -> str:
    """生成刷新令牌。"""
    return _build_token(
        subject,
        "refresh",
        expires_delta or timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )


def decode_token(token: str) -> dict[str, Any]:
    """解析令牌。"""
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])


def safe_decode_token(token: str) -> dict[str, Any] | None:
    """安全解析令牌。"""
    try:
        return decode_token(token)
    except JWTError:
        return None
