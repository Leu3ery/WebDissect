import os
import tempfile

# Configure the environment BEFORE importing the app (db engine binds at import).
_TMP = tempfile.mkdtemp(prefix="webdissect_test_")
os.environ.setdefault("DB_DIR", _TMP)
os.environ["DB_FILENAME"] = "test.db"
os.environ["JWT_SECRET"] = "test-secret"
os.environ["JWT_ALGORITHM"] = "HS256"
os.environ["RESEND_KEY"] = "RESEND_KEY"  # placeholder -> OTP logged, not sent
os.environ["EMAIL_DOMAIN"] = "htlstp.at"
os.environ["ENV"] = "test"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.server import app  # noqa: E402
from app.db.db import SessionLocal, init_db  # noqa: E402
from app.db.models.pending_verification import PendingVerification  # noqa: E402
from app.api import rate_limit  # noqa: E402

init_db()


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture(autouse=True)
def _reset_rate_limiters():
    """Isolate tests from each other's request counts."""
    for limiter in (
        rate_limit.login_limiter,
        rate_limit.register_limiter,
        rate_limit.code_limiter,
        rate_limit.scan_limiter,
    ):
        limiter._hits.clear()
    yield


def _otp_for(email: str) -> str:
    db = SessionLocal()
    try:
        pv = (
            db.query(PendingVerification)
            .filter(PendingVerification.email == email.lower())
            .first()
        )
        return pv.code if pv else ""
    finally:
        db.close()


@pytest.fixture()
def make_user(client: TestClient):
    """Factory: register + verify a user, returning (email, token)."""
    counter = {"n": 0}

    def _make(email: str | None = None) -> tuple[str, str]:
        counter["n"] += 1
        email = email or f"test.user{counter['n']}@htlstp.at"
        assert client.post("/api/auth/register", json={"email": email}).json()["isSuccess"]
        code = _otp_for(email)
        res = client.post("/api/auth/code/submit", json={"email": email, "code": code}).json()
        assert res["isSuccess"], res
        return email, res["data"]["token"]

    return _make


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}
