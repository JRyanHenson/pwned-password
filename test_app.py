from app import app


def test_health_check():
    client = app.test_client()
    response = client.get("/health")
    assert response.status_code == 200


def test_home_page():
    client = app.test_client()
    response = client.get("/tools/pwned-password/")
    assert response.status_code == 200
    assert b"pwned-password" in response.data


def test_check_empty_password():
    client = app.test_client()
    response = client.post("/tools/pwned-password/check", data={"password": ""})
    assert response.status_code == 200
    assert b"Please enter a password" in response.data
