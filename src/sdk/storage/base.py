from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import BinaryIO, Protocol


class UploadedFile(Protocol):
    """上传文件协议，解耦 FastAPI UploadFile 依赖。"""

    filename: str | None
    content_type: str | None
    file: BinaryIO


@dataclass(slots=True)
class StorageObject:
    """存储结果。"""

    original_name: str
    stored_name: str
    content_type: str | None
    size: int
    url: str


class BaseStorage(ABC):
    """存储抽象基类。"""

    @abstractmethod
    def save(self, file: UploadedFile) -> StorageObject:
        """保存文件。"""

