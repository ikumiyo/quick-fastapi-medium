from pathlib import Path
from uuid import uuid4

from src.core.config import settings
from src.core.exceptions import StorageOperationError
from src.sdk.storage.base import BaseStorage, StorageObject, UploadedFile


class LocalStorage(BaseStorage):
    """本地文件存储。"""

    def __init__(self, base_path: Path | None = None) -> None:
        self.base_path = base_path or settings.storage_path
        self.base_path.mkdir(parents=True, exist_ok=True)

    def save(self, file: UploadedFile) -> StorageObject:
        suffix = Path(file.filename or "").suffix
        stored_name = f"{uuid4().hex}{suffix}"
        destination = self.base_path / stored_name
        try:
            content = file.file.read()
            destination.write_bytes(content)
        except OSError as exc:
            raise StorageOperationError("本地文件写入失败") from exc
        return StorageObject(
            original_name=file.filename or stored_name,
            stored_name=stored_name,
            content_type=file.content_type,
            size=len(content),
            url=f"/{self.base_path.as_posix()}/{stored_name}",
        )
