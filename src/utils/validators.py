import re


def is_strong_password(password: str) -> bool:
    """校验密码强度。"""
    return bool(
        len(password) >= 8
        and re.search(r"[A-Z]", password)
        and re.search(r"[a-z]", password)
        and re.search(r"\d", password)
    )
