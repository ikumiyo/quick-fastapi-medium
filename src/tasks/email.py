import logging

logger = logging.getLogger(__name__)


def send_welcome_email(email: str) -> None:
    """发送欢迎邮件的占位函数。"""
    logger.info("send_welcome_email queued for %s", email)
