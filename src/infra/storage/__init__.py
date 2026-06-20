from src.core.config import Settings, settings
from src.infra.storage.base import BaseStorage
from src.infra.storage.local import LocalStorage
from src.infra.storage.oss import OSSStorage
from src.infra.storage.s3 import S3Storage


def build_storage_backend(app_settings: Settings | None = None) -> BaseStorage:
    """根据配置构建存储实现。"""
    current_settings = app_settings or settings
    backend = current_settings.STORAGE_BACKEND.lower()
    if backend == "s3":
        return S3Storage()
    if backend == "oss":
        return OSSStorage()
    return LocalStorage(base_path=current_settings.storage_path)
