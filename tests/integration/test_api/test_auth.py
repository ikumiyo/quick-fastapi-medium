def test_register_and_login(client):
    response = client.post(
        "/api/v1/users/",
        json={
            "email": "new-user@example.com",
            "username": "new-user",
            "full_name": "New User",
            "password": "Password123",
        },
    )
    assert response.status_code == 201
    assert response.json()["email"] == "new-user@example.com"

    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": "new-user@example.com", "password": "Password123"},
    )
    assert login_response.status_code == 200
    payload = login_response.json()
    assert payload["token_type"] == "bearer"
    assert payload["access_token"]
    assert payload["refresh_token"]


def test_get_current_user_profile(client, user_token):
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 200
    assert response.json()["username"] == "normal-user"


def test_login_returns_unified_error_payload(client, normal_user):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": normal_user.email, "password": "WrongPassword123"},
    )
    assert response.status_code == 401
    payload = response.json()
    assert payload["error"]["code"] == "INVALID_CREDENTIALS"
    assert payload["error"]["message"] == "用户名或密码错误"
    assert "request_id" in payload
