import logging

logger = logging.getLogger(__name__)


def generate_demo_report(task_id: str, username: str) -> None:
    """生成示例报表。"""
    logger.info("generate_demo_report task_id=%s username=%s", task_id, username)
