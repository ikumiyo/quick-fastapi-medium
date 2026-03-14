from uuid import uuid4

from src.schemas.task import TaskStatusResponse


class TaskService:
    """后台任务业务逻辑。"""

    def create_demo_report(
        self,
        *,
        username: str,
    ) -> TaskStatusResponse:
        task_id = uuid4().hex
        return TaskStatusResponse(
            task_id=task_id,
            status="queued",
            detail="示例报表任务已加入队列",
        )
