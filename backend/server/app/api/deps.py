from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.api.errors import Unauthorized
from app.core.security import decode_access_token
from app.db.db import get_db
from app.db.models.user import User


def get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise Unauthorized("Missing or invalid Authorization header")

    token = authorization.split(" ", 1)[1].strip()
    user_id = decode_access_token(token)
    if user_id is None:
        raise Unauthorized("Invalid or expired token")

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise Unauthorized("User no longer exists")
    return user
