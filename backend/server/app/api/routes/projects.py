from fastapi import APIRouter, UploadFile, Depends
from pydantic import BaseModel

from app.db.db import get_db

projects = APIRouter(prefix="/projects")


class CreateProject(BaseModel):
    name: str
    domain: str

class PatchProject(BaseModel):
    name: str
    domain: str



@projects.get("/{project_id}")
def get_project(project_id: int, db = Depends(get_db)):
    pass


@projects.post("")
def create_project(create_project: CreateProject, db = Depends(get_db)):
    pass


@projects.patch("/{project_id}")
def update_project(project_id: int, patch_project: PatchProject, db = Depends(get_db)):
    pass



@projects.post("/{project_id}/upload")
def upload_file(project_id: int, file: UploadFile, db = Depends(get_db)):
    pass



@projects.post("/{project_id}/analysis/start")
def start_analysis(project_id: int, db = Depends(get_db)):
    pass

