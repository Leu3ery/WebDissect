def test_login_rate_limited(client):
    payload = {"email": "nobody@htlstp.at", "password": "whatever12"}
    statuses = [client.post("/api/auth/login", json=payload).status_code for _ in range(11)]
    # First 10 are processed (401 invalid creds), the 11th is rate limited.
    assert statuses[:10] == [401] * 10
    assert statuses[10] == 429


def test_register_rate_limited(client):
    statuses = [
        client.post("/api/auth/register", json={"email": f"x.y{i}@htlstp.at"}).status_code
        for i in range(6)
    ]
    assert statuses[5] == 429
