import re
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.api.errors import ApiError
from app.config import get_settings
from app.core.email import send_otp_email
from app.core.logging import get_logger
from app.core.security import generate_otp, hash_password, verify_password
from app.db.models.pending_verification import PendingVerification
from app.db.models.user import User

logger = get_logger(__name__)

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def normalize_email(email: str) -> str:
    return (email or "").strip().lower()


def _validate_school_email(email: str) -> None:
    domain = get_settings().EMAIL_DOMAIN.lower()
    if not _EMAIL_RE.match(email) or not email.endswith("@" + domain):
        raise ApiError(f"Only {domain} email addresses are allowed")


def start_registration(db: Session, email: str) -> None:
    """Create or refresh a pending verification and email the OTP."""
    email = normalize_email(email)
    _validate_school_email(email)

    code = generate_otp()
    expires_at = datetime.utcnow() + timedelta(
        minutes=get_settings().OTP_EXPIRE_MINUTES
    )

    pending = (
        db.query(PendingVerification)
        .filter(PendingVerification.email == email)
        .first()
    )
    if pending is None:
        pending = PendingVerification(email=email)
        db.add(pending)
    pending.code = code
    pending.expires_at = expires_at
    pending.attempts = 0
    db.commit()

    send_otp_email(email, code)


def verify_code(db: Session, email: str, code: str) -> User:
    """Validate an OTP and return the (created or existing) user."""
    email = normalize_email(email)
    code = str(code).strip()

    pending = (
        db.query(PendingVerification)
        .filter(PendingVerification.email == email)
        .first()
    )
    if pending is None:
        raise ApiError("No verification in progress for this email")

    if pending.expires_at < datetime.utcnow():
        db.delete(pending)
        db.commit()
        raise ApiError("Verification code has expired")

    if pending.attempts >= get_settings().OTP_MAX_ATTEMPTS:
        db.delete(pending)
        db.commit()
        raise ApiError("Too many attempts. Please request a new code")

    if pending.code != code:
        pending.attempts += 1
        db.commit()
        raise ApiError("Invalid verification code")

    # Success - consume the pending verification.
    db.delete(pending)

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        user = User(email=email, password_hash=None)
        db.add(user)
    db.commit()
    db.refresh(user)
    logger.info("User verified via OTP: %s", email)
    return user


def login(db: Session, email: str, password: str) -> User:
    email = normalize_email(email)
    user = db.query(User).filter(User.email == email).first()
    if user is None or not user.password_hash:
        raise ApiError("Invalid email or password", status_code=401)
    if not verify_password(password, user.password_hash):
        raise ApiError("Invalid email or password", status_code=401)
    return user


def set_password(db: Session, user: User, password: str) -> None:
    if len(password) < 8:
        raise ApiError("Password must be at least 8 characters long")
    user.password_hash = hash_password(password)
    db.commit()
    logger.info("Password updated for %s", user.email)
