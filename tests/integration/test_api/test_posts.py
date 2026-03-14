def test_create_and_update_post(client, user_token):
    create_response = client.post(
        "/api/v1/posts/",
        json={
            "title": "第一篇文章",
            "summary": "摘要",
            "content": "正文内容",
            "published": False,
        },
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert create_response.status_code == 201
    post_id = create_response.json()["id"]

    update_response = client.patch(
        f"/api/v1/posts/{post_id}",
        json={"published": True},
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["published"] is True


def test_admin_dashboard_requires_admin(client, admin_token):
    response = client.get(
        "/api/v1/admin/dashboard",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert "stats" in response.json()
