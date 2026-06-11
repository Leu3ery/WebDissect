from tests.conftest import auth_headers, _otp_for


def test_register_rejects_non_school_email(client):
    res = client.post("/api/auth/register", json={"email": "foo@gmail.com"}).json()
    assert res["isSuccess"] is False
    assert "htlstp.at" in res["message"]


def test_register_and_verify_flow(client):
    email = "anna.muster@htlstp.at"
    assert client.post("/api/auth/register", json={"email": email}).json()["isSuccess"]
    res = client.post(
        "/api/auth/code/submit", json={"email": email, "code": _otp_for(email)}
    ).json()
    assert res["isSuccess"]
    assert res["data"]["token"]


def test_verify_wrong_code(client):
    email = "bob.tester@htlstp.at"
    client.post("/api/auth/register", json={"email": email})
    res = client.post(
        "/api/auth/code/submit", json={"email": email, "code": "000000"}
    ).json()
    assert res["isSuccess"] is False


def test_me_requires_auth(client):
    res = client.get("/api/auth/me")
    assert res.status_code == 401
    assert res.json()["isSuccess"] is False


def test_me_returns_user(client, make_user):
    email, token = make_user("clara.example@htlstp.at")
    res = client.get("/api/auth/me", headers=auth_headers(token)).json()
    assert res["isSuccess"]
    assert res["data"]["email"] == email
    assert "password_hash" not in res["data"]


def test_password_set_then_login(client, make_user):
    email, token = make_user("dan.example@htlstp.at")
    # No password yet -> login fails.
    assert client.post(
        "/api/auth/login", json={"email": email, "password": "supersecret"}
    ).json()["isSuccess"] is False

    # Set a password, then login works.
    assert client.patch(
        "/api/auth/me", json={"password": "supersecret"}, headers=auth_headers(token)
    ).json()["isSuccess"]
    res = client.post(
        "/api/auth/login", json={"email": email, "password": "supersecret"}
    ).json()
    assert res["isSuccess"]
    assert res["data"]["token"]


def test_short_password_rejected(client, make_user):
    _, token = make_user()
    res = client.patch(
        "/api/auth/me", json={"password": "short"}, headers=auth_headers(token)
    ).json()
    assert res["isSuccess"] is False
