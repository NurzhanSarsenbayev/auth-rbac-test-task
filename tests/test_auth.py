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