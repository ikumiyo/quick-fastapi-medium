from sqlalchemy import select
from sqlalchemy.orm import Session

from src.crud.base import CRUDBase
from src.models.file import StoredFile


class CRUDFile(CRUDBase[StoredFile]):
    """文件数据访问。"""

    def get_by_owner(
        self,
        db: Session,
        *,
        owner_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[StoredFile]:
        statement = (
            select(StoredFile)
            .where(StoredFile.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
        )
        return list(db.scalars(statement).all())


file_crud = CRUDFile(StoredFile)
