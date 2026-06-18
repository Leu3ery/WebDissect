from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.db import db_handler


auth = APIRouter(prefix="/auth")


class RegisterUser(BaseModel):
    email: str

class LoginUser(BaseModel):
    email: str
    password: str

class CodeSubmit(BaseModel):
    email: str
    code: int


@auth.post("/register", include_in_schema=False)
def register(register_user: RegisterUser):
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@auth.post("/login", include_in_schema=False)
def login(login_user: LoginUser):
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@auth.post("/code/submit", include_in_schema=False)
def submit_code(code_submit: CodeSubmit):
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@auth.patch("/me", include_in_schema=False)
def update_user():
    """
    Update user password
    """
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


