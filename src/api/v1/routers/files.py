from typing import Annotated

from fastapi import APIRouter, Depends, File, Query, UploadFile, status

from src.api.deps import FileServiceDep, get_current_active_user
from src.models.user import User
from src.schemas.file import FilePublic

router = APIRouter()


@router.post("/upload", response_model=FilePublic, status_code=status.HTTP_201_CREATED)
def upload_file(
    upload: Annotated[UploadFile, File(...)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    service: FileServiceDep,
) -> FilePublic:
    """上传文件。"""
    return service.upload(current_user=current_user, file=upload)


@router.get("/me", response_model=list[FilePublic])
def list_my_files(
    *,
    skip: Annotated[int, Query(ge=0, description="分页起始偏移量")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="单页返回条数")] = 20,
    current_user: Annotated[User, Depends(get_current_active_user)],
    service: FileServiceDep,
) -> list[FilePublic]:
    """获取当前用户上传文件。"""
    return service.list_by_owner(
        owner_id=current_user.id,
        skip=skip,
        limit=limit,
    )
