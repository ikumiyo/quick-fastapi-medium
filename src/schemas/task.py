from pydantic import BaseModel


class TaskStatusResponse(BaseModel):
    """任务响应。"""

    task_id: str
    status: str
    detail: str
