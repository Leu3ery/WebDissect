from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel

projects = APIRouter(prefix="/projects")


class CreateProject(BaseModel):
    name: str
    domain: str

class PatchProject(BaseModel):
    name: str
    domain: str



@projects.get("/{project_id}")
def get_project(project_id: int):
    pass


@projects.post("")
def create_project(create_project: CreateProject):
    pass


@projects.patch("/{project_id}")
def update_project(project_id: int, patch_project: PatchProject):
    pass



@projects.post("/{project_id}/upload")
def upload_file(project_id: int, file: UploadFile):
    pass



@projects.post("/{project_id}/analysis/start")
def start_analysis(project_id: int):
    pass

