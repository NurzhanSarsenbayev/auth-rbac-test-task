from tests.conftest import login


def test_user_cannot_access_reports_by_default(client) -> None:
    user_token = login(client, "user@example.com", "user123")

    response = client.get(
        "/mock/reports",
        headers={"Authorization": f"Bearer {user_token}"},
    )

    assert response.status_code == 403


def test_admin_can_grant_reports_access_to_user(client) -> None:
    admin_token = login(client, "admin@example.com", "admin123")
    user_token = login(client, "user@example.com", "user123")

    patch_response = client.patch(
        "/admin/permissions/6",
        json={"can_read": True, "scope": "all"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert patch_response.status_code == 200

    reports_response = client.get(
        "/mock/reports",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert reports_response.status_code == 200


def test_user_cannot_update_foreign_task(client) -> None:
    user_token = login(client, "user@example.com", "user123")

    response = client.patch(
        "/mock/tasks/1",
        json={"name": "Hacked Task"},
        headers={"Authorization": f"Bearer {user_token}"},
    )

    assert response.status_code == 403


def test_admin_can_update_any_task(client) -> None:
    admin_token = login(client, "admin@example.com", "admin123")

    response = client.patch(
        "/mock/tasks/1",
        json={"name": "Updated by admin"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Updated by admin"