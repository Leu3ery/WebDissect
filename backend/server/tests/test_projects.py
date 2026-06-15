from tests.conftest import auth_headers


def _create(client, token, name="Proj", domain="example.com"):
    return client.post(
        "/api/projects", json={"name": name, "domain": domain}, headers=auth_headers(token)
    ).json()


def test_create_and_list_projects(client, make_user):
    _, token = make_user()
    created = _create(client, token, "My Site", "example.com")
    assert created["isSuccess"]
    pid = created["data"]["id"]

    listed = client.get("/api/projects", headers=auth_headers(token)).json()
    assert listed["isSuccess"]
    assert any(p["id"] == pid for p in listed["data"])


def test_get_full_project_has_all_collections(client, make_user):
    _, token = make_user()
    pid = _create(client, token)["data"]["id"]
    res = client.get(f"/api/projects/{pid}", headers=auth_headers(token)).json()
    assert res["isSuccess"]
    for key in ("certificates", "dns_entries", "technologies", "endpoints",
                "subdomains", "ports", "path_entries"):
        assert key in res["data"]
        assert res["data"][key] == []


def test_update_project(client, make_user):
    _, token = make_user()
    pid = _create(client, token)["data"]["id"]
    res = client.patch(
        f"/api/projects/{pid}", json={"name": "Renamed"}, headers=auth_headers(token)
    ).json()
    assert res["isSuccess"]
    assert res["data"]["name"] == "Renamed"


def test_ownership_isolation(client, make_user):
    _, token_a = make_user()
    _, token_b = make_user()
    pid = _create(client, token_a)["data"]["id"]

    res = client.get(f"/api/projects/{pid}", headers=auth_headers(token_b))
    assert res.status_code == 404
    assert res.json()["isSuccess"] is False


def test_upload_har_then_endpoints_via_passive(client, make_user, monkeypatch):
    """Upload a HAR and run the passive worker (network mocked) -> endpoints persist."""
    import app.services.analysis as analysis

    # Mock all network-bound tools so the worker stays offline & deterministic.
    monkeypatch.setattr(analysis, "collect_dns", lambda domain: [])
    monkeypatch.setattr(analysis, "fetch_certificate", lambda host: None)
    monkeypatch.setattr(analysis, "fingerprint", lambda domain: [])
    monkeypatch.setattr(analysis, "enumerate_subdomains", lambda domain: [])
    monkeypatch.setattr(analysis, "security_audit", lambda domain: [])

    _, token = make_user()
    pid = _create(client, token)["data"]["id"]

    har = (
        '{"log":{"entries":[{"request":{"method":"GET","url":"https://x/a"},'
        '"response":{"status":200,"content":{"mimeType":"text/html"}}}]}}'
    )
    up = client.post(
        f"/api/projects/{pid}/upload",
        files={"file": ("c.har", har, "application/json")},
        headers=auth_headers(token),
    ).json()
    assert up["isSuccess"]

    analysis.run_passive(pid)  # synchronous worker

    res = client.get(f"/api/projects/{pid}", headers=auth_headers(token)).json()
    eps = res["data"]["endpoints"]
    assert len(eps) == 1
    assert eps[0]["path"] == "/a"


def test_har_upload_too_large(client, make_user):
    _, token = make_user()
    pid = _create(client, token)["data"]["id"]
    big = b"x" * (10 * 1024 * 1024 + 1)
    res = client.post(
        f"/api/projects/{pid}/upload",
        files={"file": ("big.har", big, "application/json")},
        headers=auth_headers(token),
    ).json()
    assert res["isSuccess"] is False
