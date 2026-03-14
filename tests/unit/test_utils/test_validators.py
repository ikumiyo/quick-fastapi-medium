from src.utils.validators import is_strong_password


def test_is_strong_password():
    assert is_strong_password("Password123") is True
    assert is_strong_password("weakpass") is False
