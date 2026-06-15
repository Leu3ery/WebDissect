import app.services.analysis as analysis
from app.api.schemas.port import Port
from app.api.schemas.path_entry import PathEntry
from app.api.schemas.subdomain import Subdomain
from app.api.schemas.technology import Technology
from app.services.analysis_hub import hub
from tests.conftest import auth_headers


def _project(client, token):
    return client.post(
        "/api/projects", json={"name": "A", "domain": "example.com"},
        headers=auth_headers(token),
    ).json()["data"]["id"]


def test_run_passive_persists_all(client, make_user, monkeypatch):
    from app.api.schemas.dns_entry import DNSEntry, EntryType

    monkeypatch.setattr(analysis, "collect_dns",
                        lambda d: [DNSEntry(type=EntryType.IPv4, domain=d, value="1.2.3.4", ttl=60)])
    monkeypatch.setattr(analysis, "fetch_certificate", lambda host: None)
    monkeypatch.setattr(analysis, "fingerprint",
                        lambda d: [Technology(name="Nginx", description="srv", icon_url="x")])
    monkeypatch.setattr(analysis, "enumerate_subdomains",
                        lambda d: [Subdomain(name="api.example.com", ip="1.2.3.4", source="crt.sh")])
    monkeypatch.setattr(analysis, "security_audit", lambda d: [])

    _, token = make_user()
    pid = _project(client, token)
    analysis.run_passive(pid)

    data = client.get(f"/api/projects/{pid}", headers=auth_headers(token)).json()["data"]
    assert len(data["dns_entries"]) == 1
    assert len(data["technologies"]) == 1
    assert data["subdomains"][0]["name"] == "api.example.com"
    # Hub marks the run finished.
    assert hub.snapshot(pid)["running"] is False


def test_run_port_scan_persists(client, make_user, monkeypatch):
    monkeypatch.setattr(analysis, "scan_ports",
                        lambda d, on_progress=None: [Port(port=443, service="https", version="nginx")])
    _, token = make_user()
    pid = _project(client, token)
    analysis.run_port_scan(pid)

    ports = client.get(f"/api/projects/{pid}", headers=auth_headers(token)).json()["data"]["ports"]
    assert ports[0]["port"] == 443
    assert ports[0]["service"] == "https"


def test_run_path_scan_persists(client, make_user, monkeypatch):
    monkeypatch.setattr(analysis, "enumerate_paths",
                        lambda d, on_progress=None: [PathEntry(path="/admin", status=200, content_type="text/html")])
    _, token = make_user()
    pid = _project(client, token)
    analysis.run_path_scan(pid)

    paths = client.get(f"/api/projects/{pid}", headers=auth_headers(token)).json()["data"]["path_entries"]
    assert paths[0]["path"] == "/admin"
    assert paths[0]["status"] == 200
