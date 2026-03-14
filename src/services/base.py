from sqlalchemy.orm import Session

from src.crud.base import CRUDBase


class BaseService[CRUDType: CRUDBase]:
    """服务基类。"""

    def __init__(self, crud: CRUDType, db: Session) -> None:
        self.crud = crud
        self.db = db
