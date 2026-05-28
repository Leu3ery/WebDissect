from fastapi import APIRouter

auth = APIRouter(prefix="/auth")


@auth.post("/register")
def register():
    pass


@auth.post("/login")
def login():
    pass


@auth.post("/code/submit")
def submit_code():
    pass


@auth.patch("/me")
def update_user():
    """
    Update user password
    """
    pass


