from tests.conftest import login


def test_login_success(client) -> None:
    token = login(client, "admin@example.com", "admin123")
    assert token


def test_logout_revokes_token(client) -> None:
    token = login(client, "admin@example.com", "admin123")

    me_response_before_logout = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_response_before_logout.status_code == 200

    logout_response = client.post(
        "/auth/logout",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert logout_response.status_code == 200
    assert logout_response.json()["message"] == "Successfully logged out."

    me_response_after_logout = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_response_after_logout.status_code == 401
    assert me_response_after_logout.json()["detail"] == "Token has been revoked."

def test_delete_me_revokes_token(client):
    login_response = client.post(
        "/auth/login",
        json={"email": "user@example.com", "password": "user123"},
    )
    access_token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    delete_response = client.delete("/users/me", headers=headers)
    assert delete_response.status_code == 204

    me_response = client.get("/users/me", headers=headers)
    assert me_response.status_code == 401
    assert me_response.json()["detail"] == "Token has been revoked."


def test_deleted_user_cannot_login(client):
    login_response = client.post(
        "/auth/login",
        json={"email": "user@example.com", "password": "user123"},
    )
    access_token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    delete_response = client.delete("/users/me", headers=headers)
    assert delete_response.status_code == 204

    relogin_response = client.post(
        "/auth/login",
        json={"email": "user@example.com", "password": "user123"},
    )
    assert relogin_response.status_code == 403
    assert relogin_response.json()["detail"] == "User is inactive or deleted."