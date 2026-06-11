from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.rate_limit import code_limiter, login_limiter, register_limiter
from app.api.response import ApiResponse, ok
from app.api.schemas.responses import TokenRead, UserRead
from app.core.security import create_access_token
from app.db.db import get_db
from app.db.models.user import User
from app.services import users as users_service

auth = APIRouter(prefix="/auth", tags=["auth"])


class RegisterUser(BaseModel):
    email: str


class LoginUser(BaseModel):
    email: str
    password: str


class CodeSubmit(BaseModel):
    email: str
    code: str


class UpdatePassword(BaseModel):
    password: str


@auth.post("/register", dependencies=[Depends(register_limiter)])
def register(body: RegisterUser, db: Session = Depends(get_db)) -> ApiResponse[None]:
    users_service.start_registration(db, body.email)
    return ok(None, "Verification code sent")


@auth.post("/code/submit", dependencies=[Depends(code_limiter)])
def submit_code(body: CodeSubmit, db: Session = Depends(get_db)) -> ApiResponse[TokenRead]:
    user = users_service.verify_code(db, body.email, body.code)
    token = create_access_token(user.id)
    return ok(TokenRead(token=token), "Verification successful")


@auth.post("/login", dependencies=[Depends(login_limiter)])
def login(body: LoginUser, db: Session = Depends(get_db)) -> ApiResponse[TokenRead]:
    user = users_service.login(db, body.email, body.password)
    token = create_access_token(user.id)
    return ok(TokenRead(token=token), "Logged in")


@auth.get("/me")
def get_me(user: User = Depends(get_current_user)) -> ApiResponse[UserRead]:
    return ok(UserRead.model_validate(user))


@auth.patch("/me")
def update_user(
    body: UpdatePassword,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ApiResponse[None]:
    """Update (set) the current user's password."""
    users_service.set_password(db, user, body.password)
    return ok(None, "Password updated")
