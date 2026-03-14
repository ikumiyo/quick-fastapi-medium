from sqlalchemy.orm import Session

from src.crud.file import CRUDFile
from src.models.file import StoredFile
from src.models.user import User
from src.sdk.storage.base import BaseStorage, UploadedFile
from src.services.base import BaseService


class FileService(BaseService[CRUDFile]):
    """文件业务逻辑。"""

    def __init__(self, crud: CRUDFile, db: Session, storage: BaseStorage) -> None:
        super().__init__(crud, db)
        self.storage = storage

    def upload(
        self,
        *,
        current_user: User,
        file: UploadedFile,
    ) -> StoredFile:
        storage_object = self.storage.save(file)
        return self.crud.create(
            self.db,
            obj_in={
                "original_name": storage_object.original_name,
                "stored_name": storage_object.stored_name,
                "content_type": storage_object.content_type,
                "size": storage_object.size,
                "url": storage_object.url,
                "owner_id": current_user.id,
            },
        )

    def list_by_owner(
        self,
        *,
        owner_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[StoredFile]:
        return self.crud.get_by_owner(self.db, owner_id=owner_id, skip=skip, limit=limit)
