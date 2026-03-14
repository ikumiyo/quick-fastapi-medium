import logging

logger = logging.getLogger(__name__)


def export_posts_snapshot(task_id: str) -> None:
    """导出文章快照。"""
    logger.info("export_posts_snapshot task_id=%s", task_id)
