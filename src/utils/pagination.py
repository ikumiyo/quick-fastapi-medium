def get_pagination_meta(*, skip: int, limit: int, total: int) -> dict[str, int]:
    """生成分页元信息。"""
    return {"skip": skip, "limit": limit, "total": total}
