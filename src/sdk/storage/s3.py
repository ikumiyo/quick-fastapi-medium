from src.sdk.storage.base import BaseStorage, StorageObject, UploadedFile


class S3Storage(BaseStorage):
    """S3 存储占位实现。"""

    def save(self, file: UploadedFile) -> StorageObject:
        raise NotImplementedError("当前模板未启用 S3 存储，请切换到 local 或自行补充实现")
