from typing import Any

from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.core.exceptions import DatabaseOperationError
from src.models.base import Base


class CRUDBase[ModelType: Base]:
    """基础 CRUD。"""

    def __init__(self, model: type[ModelType]) -> None:
        self.model = model

    def get(self, db: Session, item_id: Any) -> ModelType | None:
        """根据主键获取记录。"""
        return db.get(self.model, item_id)

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: dict[str, Any] | None = None,
    ) -> list[ModelType]:
        """分页获取多条记录。"""
        statement = select(self.model)
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    statement = statement.where(getattr(self.model, field) == value)
        statement = statement.offset(skip).limit(limit)
        return list(db.scalars(statement).all())

    def count(self, db: Session, filters: dict[str, Any] | None = None) -> int:
        """统计数量。"""
        statement = select(func.count()).select_from(self.model)
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    statement = statement.where(getattr(self.model, field) == value)
        return int(db.scalar(statement) or 0)

    def create(self, db: Session, *, obj_in: BaseModel | dict[str, Any]) -> ModelType:
        """创建记录。"""
        data = obj_in.model_dump() if isinstance(obj_in, BaseModel) else dict(obj_in)
        db_obj = self.model(**data)
        try:
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        except SQLAlchemyError as exc:
            db.rollback()
            raise DatabaseOperationError("数据库写入失败") from exc
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: BaseModel | dict[str, Any],
    ) -> ModelType:
        """更新记录。"""
        update_data = (
            obj_in.model_dump(exclude_unset=True)
            if isinstance(obj_in, BaseModel)
            else obj_in
        )
        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        try:
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        except SQLAlchemyError as exc:
            db.rollback()
            raise DatabaseOperationError("数据库更新失败") from exc
        return db_obj

    def delete(self, db: Session, *, item_id: Any) -> ModelType | None:
        """删除记录。"""
        obj = self.get(db, item_id)
        if obj is None:
            return None
        try:
            db.delete(obj)
            db.commit()
        except SQLAlchemyError as exc:
            db.rollback()
            raise DatabaseOperationError("数据库删除失败") from exc
        return obj
