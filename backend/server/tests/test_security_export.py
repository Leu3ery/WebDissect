import app.services.analysis as analysis
from app.tools._security import audit_headers
from app.tools._paths import is_soft_404, Response, Baseline, is_interesting
from tests.conftest import auth_headers


# --- security header audit (pure) ----------------------------------------

def test_audit_headers_flags_missing_and_present():
    checks = {c.name: c for c in audit_headers({
        "content-security-policy": "default-src 'self'",
        "server": "nginx/1.25.3",
    })}
    assert checks["Content-Security-Policy"].status == "ok"
    assert checks["Strict-Transport-Security"].status == "fail"
    assert checks["Server disclosure"].status == "warn"


def test_audit_headers_frame_ancestors_covers_xfo():
    checks = {c.name: c for c in audit_headers(
        {"content-security-policy": "frame-ancestors 'none'"}
    )}
    assert checks["X-Frame-Options"].status == "ok"


def test_audit_headers_cookie_flags():
    checks = {c.name: c for c in audit_headers({"set-cookie": "sid=1; Path=/"})}
    assert checks["Cookie flags"].status == "warn"
    assert "HttpOnly" in checks["Cookie flags"].detail


# --- soft-404 detection (pure) -------------------------------------------

def test_is_soft_404_matches_baseline():
    baseline = Baseline(status=200, length=1000, sample="Not Found")
    assert is_soft_404(Response(200, "text/html", 1000, "Not Found"), baseline)
    assert is_soft_404(Response(200, "text/html", 1010, "different"), baseline)  # length within tolerance


def test_is_soft_404_real_hit_differs():
    baseline = Baseline(status=200, length=1000, sample="Not Found")
    assert not is_soft_404(Response(200, "text/html", 5000, "real page"), baseline)
    assert not is_soft_404(Response(200, "text/html", 1000, "x"), None)


def test_is_interesting_excludes_404():
    assert is_interesting(200) and not is_interesting(404)


# --- history + export endpoints ------------------------------------------

def _project(client, token):
    return client.post(
        "/api/projects", json={"name": "Exp", "domain": "example.com"},
        headers=auth_headers(token),
    ).json()["data"]["id"]


def _mock_offline(monkeypatch):
    monkeypatch.setattr(analysis, "collect_dns", lambda d: [])
    monkeypatch.setattr(analysis, "fetch_certificate", lambda h: None)
    monkeypatch.setattr(analysis, "fingerprint", lambda d: [])
    monkeypatch.setattr(analysis, "enumerate_subdomains", lambda d: [])
    monkeypatch.setattr(analysis, "security_audit", lambda d: [])


def test_history_records_runs(client, make_user, monkeypatch):
    _mock_offline(monkeypatch)
    _, token = make_user()
    pid = _project(client, token)

    analysis.run_passive(pid)
    analysis.run_passive(pid)

    res = client.get(f"/api/projects/{pid}/history", headers=auth_headers(token)).json()
    assert res["isSuccess"]
    assert len(res["data"]) == 2
    assert "dns" in res["data"][0]["counts"]


def test_export_json(client, make_user):
    _, token = make_user()
    pid = _project(client, token)
    res = client.get(f"/api/projects/{pid}/export/json", headers=auth_headers(token))
    assert res.status_code == 200
    assert res.headers["content-type"].startswith("application/json")
    assert "attachment" in res.headers["content-disposition"]
    assert res.json()["domain"] == "example.com"


def test_export_pdf(client, make_user):
    _, token = make_user()
    pid = _project(client, token)
    res = client.get(f"/api/projects/{pid}/export/pdf", headers=auth_headers(token))
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/pdf"
    assert res.content[:4] == b"%PDF"
