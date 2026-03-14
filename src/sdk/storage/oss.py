from src.sdk.storage.base import BaseStorage, StorageObject, UploadedFile


class OSSStorage(BaseStorage):
    """OSS 存储占位实现。"""

    def save(self, file: UploadedFile) -> StorageObject:
        raise NotImplementedError("当前模板未启用 OSS 存储，请切换到 local 或自行补充实现")
