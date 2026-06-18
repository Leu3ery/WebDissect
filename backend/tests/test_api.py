import sys
import socket
import threading
import time
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterator

import pytest
import requests
import uvicorn
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker


SERVER_DIR = Path(__file__).resolve().parents[1] / "server"
if str(SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(SERVER_DIR))


class _TestDBHandler:
    def __init__(self, db_path: Path):
        from app.db.models import Base

        self.engine = create_engine(
            f"sqlite:///{db_path}",
            connect_args={"check_same_thread": False},
        )
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine,
        )
        Base.metadata.create_all(self.engine)

    @contextmanager
    def transaction(self) -> Iterator[Session]:
        from app.db import DBConnectionError, DBError, DBIntegrityError

        db = self.SessionLocal()
        try:
            yield db
            db.commit()
        except IntegrityError as exc:
            db.rollback()
            raise DBIntegrityError(str(exc.orig)) from exc
        except OperationalError as exc:
            db.rollback()
            raise DBConnectionError(str(exc.orig)) from exc
        except SQLAlchemyError as exc:
            db.rollback()
            raise DBError(str(exc)) from exc
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()


class APIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def get(self, path: str, **kwargs):
        return requests.get(f"{self.base_url}{path}", timeout=10, **kwargs)

    def post(self, path: str, **kwargs):
        return requests.post(f"{self.base_url}{path}", timeout=10, **kwargs)

    def patch(self, path: str, **kwargs):
        return requests.patch(f"{self.base_url}{path}", timeout=10, **kwargs)


def get_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@pytest.fixture()
def client(tmp_path, monkeypatch) -> Iterator[APIClient]:
    monkeypatch.setenv("RESEND_KEY", "test")
    monkeypatch.setenv("JWT_ALGORITHM", "HS256")
    monkeypatch.setenv("JWT_SECRET", "secret")
    monkeypatch.setenv("DB_FILENAME", "test.db")
    monkeypatch.setenv("HAR_STORAGE_DIR", "har_files")

    import app.db as app_db
    import app.api.routes.projects as project_routes
    import app.api.routes.tools as tool_routes
    from app.db.models import User
    from app.server import app

    db_handler = _TestDBHandler(tmp_path / "api.db")
    monkeypatch.setattr(app_db, "db_handler", db_handler)
    monkeypatch.setattr(project_routes, "db_handler", db_handler)
    monkeypatch.setattr(tool_routes, "db_handler", db_handler)
    monkeypatch.setattr(project_routes, "UPLOAD_DIR", tmp_path / "har_files")

    with db_handler.transaction() as db:
        db.add(User(id=1, email="tester@example.com", password_hash="hash"))

    def fake_fetch_dns(domain: str, analysis_id: int) -> None:
        from app.db.models import Analysis, DNSEntry

        with db_handler.transaction() as db:
            db.add(DNSEntry(
                analysis_id=analysis_id,
                type="A",
                domain=domain,
                value="93.184.216.34",
                ttl=300,
            ))
            db.get(Analysis, analysis_id).is_dns_analysis_completed = True

    def fake_fetch_cert(domain: str, analysis_id: int) -> None:
        from app.db.models import Analysis, Certificate

        now = datetime.utcnow()
        with db_handler.transaction() as db:
            db.add(Certificate(
                analysis_id=analysis_id,
                subject_domain=domain,
                subject_organization="Example Org",
                subject_country="AT",
                issuer_name="Example CA",
                issuer_organization="Example CA Org",
                issuer_country="AT",
                valid_from=now,
                valid_to=now + timedelta(days=90),
                serial_number=f"{analysis_id:040d}",
                public_key_type="RSA",
                fingerprint_sha256=f"{analysis_id:064x}",
            ))
            db.get(Analysis, analysis_id).is_cert_analysis_completed = True

    monkeypatch.setattr(project_routes, "_fetch_dns", fake_fetch_dns)
    monkeypatch.setattr(project_routes, "_fetch_cert", fake_fetch_cert)

    port = get_free_port()
    config = uvicorn.Config(
        app,
        host="127.0.0.1",
        port=port,
        log_level="warning",
        lifespan="off",
    )
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    deadline = time.time() + 10
    while not server.started:
        if time.time() > deadline:
            raise RuntimeError("Timed out waiting for test API server to start")
        time.sleep(0.05)

    try:
        yield APIClient(f"http://127.0.0.1:{port}")
    finally:
        server.should_exit = True
        thread.join(timeout=10)


def assert_base_response(response, status_code: int = 200):
    assert response.status_code == status_code, response.text
    payload = response.json()
    assert payload["isSuccess"] is True
    assert payload["errorMessage"] is None
    return payload["data"]


def create_project(client: APIClient, name: str = "Test", domain: str = "example.com") -> int:
    data = assert_base_response(client.post("/api/projects", json={
        "name": name,
        "domain": domain,
    }))
    return data["projectId"]


def test_auth_endpoints_are_not_implemented(client: APIClient):
    requests = [
        ("post", "/api/auth/register", {"email": "tester@example.com"}),
        ("post", "/api/auth/login", {"email": "tester@example.com", "password": "secret"}),
        ("post", "/api/auth/code/submit", {"email": "tester@example.com", "code": 123456}),
        ("patch", "/api/auth/me", None),
    ]

    for method, path, body in requests:
        response = getattr(client, method)(path, json=body) if body else getattr(client, method)(path)
        assert response.status_code == 501


def test_get_projects_returns_empty_list(client: APIClient):
    assert assert_base_response(client.get("/api/projects")) == []


def test_create_project_normalizes_domain_and_get_projects_returns_it(client: APIClient):
    project_id = create_project(client, name="Example", domain="EXAMPLE.COM.")

    projects = assert_base_response(client.get("/api/projects"))

    assert projects == [{
        "project": {
            "id": project_id,
            "name": "Example",
            "domain": "example.com",
            "user_id": 1,
        },
        "analysis_id": None,
    }]


@pytest.mark.parametrize("domain", ["localhost", "www.example.com"])
def test_create_project_rejects_invalid_domains(client: APIClient, domain: str):
    response = client.post("/api/projects", json={
        "name": "Bad Domain",
        "domain": domain,
    })

    assert response.status_code == 422


def test_update_project_updates_name_and_domain(client: APIClient):
    project_id = create_project(client)

    data = assert_base_response(client.patch(f"/api/projects/{project_id}", json={
        "name": "Updated",
        "domain": "openai.com",
    }))
    assert data is None

    project = assert_base_response(client.get("/api/projects"))[0]["project"]
    assert project["name"] == "Updated"
    assert project["domain"] == "openai.com"


def test_update_project_with_empty_payload_returns_server_error(client: APIClient):
    project_id = create_project(client)

    response = client.patch(f"/api/projects/{project_id}", json={})

    assert response.status_code == 500


def test_upload_har_accepts_valid_har(client: APIClient, tmp_path, monkeypatch):
    import app.api.routes.projects as project_routes

    project_id = create_project(client)
    har_path = tmp_path / "capture.har"
    har_path.write_text(
        '{"log": {"version": "1.2", "entries": [{}, {}]}}',
        encoding="utf-8",
    )
    monkeypatch.setattr(project_routes, "validate_har", lambda path: 2)

    with har_path.open("rb") as har:
        data = assert_base_response(client.post(
            f"/api/projects/{project_id}/upload",
            files={"file": ("capture.har", har, "application/json")},
        ))

    assert data == {"entryCount": 2}


def test_upload_har_rejects_unknown_project(client: APIClient, tmp_path):
    har_path = tmp_path / "capture.har"
    har_path.write_text('{"log": {"entries": []}}', encoding="utf-8")

    with har_path.open("rb") as har:
        response = client.post(
            "/api/projects/999/upload",
            files={"file": ("capture.har", har, "application/json")},
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"


def test_upload_har_rejects_non_har_extension(client: APIClient, tmp_path):
    project_id = create_project(client)
    upload_path = tmp_path / "capture.json"
    upload_path.write_text("{}", encoding="utf-8")

    with upload_path.open("rb") as upload:
        response = client.post(
            f"/api/projects/{project_id}/upload",
            files={"file": ("capture.json", upload, "application/json")},
        )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid file format. Only .har files allowed."


def test_upload_har_rejects_invalid_json(client: APIClient, tmp_path):
    project_id = create_project(client)
    har_path = tmp_path / "broken.har"
    har_path.write_text("{not-json", encoding="utf-8")

    with har_path.open("rb") as har:
        response = client.post(
            f"/api/projects/{project_id}/upload",
            files={"file": ("broken.har", har, "application/json")},
        )

    assert response.status_code == 422
    assert response.json()["detail"] == "Not a valid HAR file"


def test_start_analysis_creates_analysis_and_tool_results(client: APIClient):
    project_id = create_project(client)

    start_data = assert_base_response(client.post(f"/api/projects/{project_id}/analysis/start"))
    analysis_id = start_data["analysisId"]

    projects = assert_base_response(client.get("/api/projects"))
    assert projects[0]["analysis_id"] == analysis_id

    dns_entries = client.get(f"/api/dns/{analysis_id}")
    assert dns_entries.status_code == 200
    assert dns_entries.json() == [{
        "id": 1,
        "type": "A",
        "domain": "example.com",
        "value": "93.184.216.34",
        "ttl": 300,
    }]

    certificate = client.get(f"/api/tls/{analysis_id}")
    assert certificate.status_code == 200
    cert_payload = certificate.json()
    assert cert_payload["subject_domain"] == "example.com"
    assert cert_payload["issuer_name"] == "Example CA"
    assert cert_payload["fingerprint_sha256"] == f"{analysis_id:064x}"


def test_start_analysis_rejects_unknown_project(client: APIClient):
    response = client.post("/api/projects/999/analysis/start")

    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"


def test_tools_return_empty_results_for_unknown_analysis(client: APIClient):
    dns_response = client.get("/api/dns/999")
    tls_response = client.get("/api/tls/999")

    assert dns_response.status_code == 200
    assert dns_response.json() == []
    assert tls_response.status_code == 200
    assert tls_response.json() is None
