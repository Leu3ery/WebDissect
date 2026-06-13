from fastapi import APIRouter, Depends
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


@auth.post("/register")
def register(register_user: RegisterUser):
    pass


@auth.post("/login")
def login(login_user: LoginUser):
    pass


@auth.post("/code/submit")
def submit_code(code_submit: CodeSubmit):
    pass


@auth.patch("/me")
def update_user():
    """
    Update user password
    """
    pass


