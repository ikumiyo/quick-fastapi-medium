from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, status

from src.api.deps import TaskServiceDep, get_current_active_user
from src.models.user import User
from src.schemas.task import TaskStatusResponse
from src.tasks.report import generate_demo_report

router = APIRouter()


@router.post(
    "/reports/demo",
    response_model=TaskStatusResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def create_demo_report(
    background_tasks: BackgroundTasks,
    current_user: Annotated[User, Depends(get_current_active_user)],
    service: TaskServiceDep,
) -> TaskStatusResponse:
    """创建示例后台任务。"""
    task = service.create_demo_report(username=current_user.username)
    background_tasks.add_task(generate_demo_report, task.task_id, current_user.username)
    return task
