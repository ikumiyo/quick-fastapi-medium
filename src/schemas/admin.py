from pydantic import BaseModel


class AdminDashboardStats(BaseModel):
    """管理员概览统计。"""

    users: int
    posts: int
    published_posts: int
    files: int


class AdminDashboardResponse(BaseModel):
    """管理员概览响应。"""

    message: str
    stats: AdminDashboardStats
