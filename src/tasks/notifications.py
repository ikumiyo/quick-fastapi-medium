import logging

logger = logging.getLogger(__name__)


def push_admin_notification(message: str) -> None:
    """推送后台通知。"""
    logger.info("push_admin_notification message=%s", message)
