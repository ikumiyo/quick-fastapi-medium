from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.v1.api import api_router
from src.core.config import settings
from src.core.events import on_shutdown, on_startup
from src.core.exceptions import add_exception_handlers
from src.middleware.request_id import RequestIDMiddleware
from src.middleware.timing import TimingMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """统一管理应用生命周期。"""
    on_startup(app)
    yield
    on_shutdown(app)


def get_application() -> FastAPI:
    """创建并配置 FastAPI 应用。"""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        debug=settings.DEBUG,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(TimingMiddleware)

    add_exception_handlers(app)
    app.include_router(api_router, prefix=settings.API_V1_STR)

    @app.get("/", tags=["system"])
    def root() -> dict[str, str]:
        """根路由健康检查。"""
        return {"message": f"{settings.PROJECT_NAME} is running"}

    @app.get("/health", tags=["system"])
    def health() -> dict[str, str]:
        """标准健康检查。"""
        return {"status": "ok"}

    return app


app = get_application()
