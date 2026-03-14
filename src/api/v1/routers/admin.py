from typing import Annotated

from fastapi import APIRouter, Depends

from src.api.deps import AdminServiceDep, require_admin
from src.models.user import User
from src.schemas.admin import AdminDashboardResponse

router = APIRouter()


@router.get("/dashboard", response_model=AdminDashboardResponse)
def get_admin_dashboard(
    current_user: Annotated[User, Depends(require_admin)],
    service: AdminServiceDep,
) -> AdminDashboardResponse:
    """管理员概览。"""
    return service.get_dashboard(current_user=current_user)
