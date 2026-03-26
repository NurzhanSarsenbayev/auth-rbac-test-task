from tests.conftest import login


def test_login_success(client) -> None:
    token = login(client, "admin@example.com", "admin123")
    assert token