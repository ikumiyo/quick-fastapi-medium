from fastapi import APIRouter

from src.api.v1.routers import admin, auth, files, posts, tasks, users

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(posts.router, prefix="/posts", tags=["posts"])
api_router.include_router(files.router, prefix="/files", tags=["files"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
