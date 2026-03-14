import logging
from typing import Any

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class AppError(Exception):
    """应用异常基类。"""

    code = "APP_ERROR"
    http_status = status.HTTP_400_BAD_REQUEST
    log_level = logging.WARNING

    def __init__(self, message: str | None = None) -> None:
        self.message = message or self.__class__.__name__
        super().__init__(self.message)


class DomainError(AppError):
    """领域异常基类。"""


class InfrastructureError(AppError):
    """基础设施异常基类。"""

    code = "INFRASTRUCTURE_ERROR"
    http_status = status.HTTP_502_BAD_GATEWAY
    log_level = logging.ERROR


class DatabaseOperationError(InfrastructureError):
    """数据库操作失败。"""

    code = "DATABASE_ERROR"
    message = "数据库操作失败"


class RedisOperationError(InfrastructureError):
    """Redis 操作失败。"""

    code = "REDIS_ERROR"
    message = "Redis 操作失败"


class StorageOperationError(InfrastructureError):
    """存储操作失败。"""

    code = "STORAGE_ERROR"
    message = "存储操作失败"


class ValidationFailedError(AppError):
    """请求参数校验失败。"""

    code = "VALIDATION_ERROR"
    http_status = status.HTTP_422_UNPROCESSABLE_ENTITY


class AuthenticationError(DomainError):
    """认证失败。"""

    code = "AUTHENTICATION_FAILED"
    http_status = status.HTTP_401_UNAUTHORIZED


class AccountDisabledError(DomainError):
    """账号已被禁用。"""

    code = "ACCOUNT_DISABLED"
    http_status = status.HTTP_403_FORBIDDEN


class PermissionDeniedError(DomainError):
    """权限不足。"""

    code = "PERMISSION_DENIED"
    http_status = status.HTTP_403_FORBIDDEN


class ConflictError(DomainError):
    """资源冲突。"""

    code = "CONFLICT"
    http_status = status.HTTP_409_CONFLICT


class UserNotFoundError(DomainError):
    """用户不存在。"""

    code = "USER_NOT_FOUND"
    http_status = status.HTTP_404_NOT_FOUND


class EmailAlreadyExistsError(ConflictError):
    """邮箱已存在。"""

    code = "EMAIL_ALREADY_EXISTS"


class UsernameAlreadyExistsError(ConflictError):
    """用户名已存在。"""

    code = "USERNAME_ALREADY_EXISTS"


class PostNotFoundError(DomainError):
    """文章不存在。"""

    code = "POST_NOT_FOUND"
    http_status = status.HTTP_404_NOT_FOUND


class InvalidCredentialsError(AuthenticationError):
    """用户名或密码错误。"""

    code = "INVALID_CREDENTIALS"


class TokenInvalidError(AuthenticationError):
    """令牌无效。"""

    code = "TOKEN_INVALID"


class TokenTypeError(AuthenticationError):
    """令牌类型错误。"""

    code = "TOKEN_TYPE_INVALID"


class TokenSubjectMissingError(AuthenticationError):
    """令牌主体缺失。"""

    code = "TOKEN_SUBJECT_MISSING"


class RefreshTokenRevokedError(AuthenticationError):
    """刷新令牌已失效。"""

    code = "REFRESH_TOKEN_REVOKED"


def _build_error_payload(request: Request, code: str, message: str) -> dict[str, Any]:
    """构造统一错误响应。"""
    return {
        "error": {
            "code": code,
            "message": message,
        },
        "request_id": getattr(request.state, "request_id", None),
    }


def _log_request_error(
    request: Request,
    *,
    level: int,
    code: str,
    message: str,
    exc: Exception | None = None,
) -> None:
    """在 API 边界统一记录异常日志。"""
    extra = {
        "error_code": code,
        "path": request.url.path,
        "method": request.method,
    }
    log_message = "request_failed"
    if level >= logging.ERROR and exc is not None:
        logger.exception(log_message, exc_info=exc, extra=extra)
        return
    logger.log(level, log_message, extra=extra)


def _map_http_exception(exc: HTTPException) -> tuple[str, str, int]:
    """将框架 HTTP 异常映射为统一错误协议。"""
    status_map = {
        status.HTTP_401_UNAUTHORIZED: "UNAUTHORIZED",
        status.HTTP_403_FORBIDDEN: "FORBIDDEN",
        status.HTTP_404_NOT_FOUND: "NOT_FOUND",
        status.HTTP_409_CONFLICT: "CONFLICT",
    }
    code = status_map.get(exc.status_code, "HTTP_ERROR")
    message = exc.detail if isinstance(exc.detail, str) else "请求处理失败"
    return code, message, exc.status_code


def add_exception_handlers(app: FastAPI) -> None:
    """注册全局异常处理器。"""

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        # 统一处理项目业务异常
        # 日志级别按异常本身定义，错误级别及以上记录完整异常链
        _log_request_error(
            request,
            level=exc.log_level,
            code=exc.code,
            message=exc.message,
            exc=exc if exc.log_level >= logging.ERROR else None,
        )
        # 返回统一错误响应结构
        return JSONResponse(
            status_code=exc.http_status,
            content=_build_error_payload(request, exc.code, exc.message),
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        # 统一处理 FastAPI/Starlette 框架自身的 HTTPException
        code, message, http_status = _map_http_exception(exc)
        # 500 以上为 error，否则 warning
        level = logging.ERROR if http_status >= 500 else logging.WARNING
        _log_request_error(
            request,
            level=level,
            code=code,
            message=message,
            exc=exc if level >= logging.ERROR else None,
        )
        # 注意透传原始 headers（如认证场景）
        return JSONResponse(
            status_code=http_status,
            content=_build_error_payload(request, code, message),
            headers=exc.headers,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        _: RequestValidationError,
    ) -> JSONResponse:
        # 处理参数校验异常，转换为 ValidationFailedError
        validation_error = ValidationFailedError("请求参数校验失败")
        _log_request_error(
            request,
            level=validation_error.log_level,
            code=validation_error.code,
            message=validation_error.message,
        )
        return JSONResponse(
            status_code=validation_error.http_status,
            content=_build_error_payload(
                request,
                validation_error.code,
                validation_error.message,
            ),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        # 捕获一切未被前面 handler 覆盖的异常（兜底，避免接口 500 无详细输出）
        _log_request_error(
            request,
            level=logging.ERROR,
            code="INTERNAL_SERVER_ERROR",
            message="服务器内部错误",
            exc=exc,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_build_error_payload(
                request,
                "INTERNAL_SERVER_ERROR",
                "服务器内部错误",
            ),
        )
