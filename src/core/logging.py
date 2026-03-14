import json
import logging
from logging.config import dictConfig

from src.core.config import settings
from src.middleware.request_id import get_request_id


class RequestIDFilter(logging.Filter):
    """将 request_id 注入日志记录。"""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = get_request_id()
        return True


class JsonFormatter(logging.Formatter):
    """输出 JSON 结构化日志。"""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", None),
            "error_code": getattr(record, "error_code", None),
            "path": getattr(record, "path", None),
            "method": getattr(record, "method", None),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def configure_logging() -> None:
    """配置应用日志。"""
    # 根据配置选择日志格式，支持 "json" 或 "plain"（普通文本）
    formatter = "json" if settings.LOG_FORMAT.lower() == "json" else "plain"

    # 普通文本日志格式定义，包括时间、等级、logger名、request_id和消息内容
    plain_format = "%(asctime)s | %(levelname)s | %(name)s | %(request_id)s | %(message)s"
    
    # 日志处理器（handler）配置字典
    handlers: dict[str, dict[str, object]] = {
        "default": {
            "class": "logging.StreamHandler",         # 默认使用标准输出流
            "filters": ["request_id"],                # 注入 request_id
            "formatter": formatter,                   # 使用上面选择的格式化器
        }
    }

    # 如果是开发环境且允许写日志文件，则添加文件处理器（file handler）
    if settings.ENVIRONMENT.lower() == "development" and settings.LOG_FILE_ENABLED:
        settings.log_file_path.parent.mkdir(parents=True, exist_ok=True)  # 确保日志目录存在
        handlers["json_file"] = {
            "class": "logging.FileHandler",           # 写入文件
            "filename": str(settings.log_file_path),  # 日志文件路径
            "encoding": "utf-8",                      # 文件编码
            "filters": ["request_id"],                # 同样注入 request_id
            "formatter": "json",                      # 文件强制使用 json 格式方便采集
        }

    # 最终用于 root logger 的 handler 名称列表
    root_handlers = list(handlers.keys())

    # 配置 logging，包括过滤器、格式化器、处理器及根 logger
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,              # 不禁用已存在的 logger（如uvicorn内部）
            "filters": {
                "request_id": {
                    "()": RequestIDFilter,                 # 自定义的 request_id 过滤器
                }
            },
            "formatters": {
                "plain": {
                    "format": plain_format,                # 普通文本格式
                },
                "json": {
                    "()": JsonFormatter,                   # 自定义的 json 格式化器，输出结构化日志
                },
            },
            "handlers": handlers,                          # 上面定义好的所有 handler
            "root": {
                "handlers": root_handlers,                 # 绑定给 root logger
                "level": settings.LOG_LEVEL.upper(),       # 日志等级
            },
        }
    )
