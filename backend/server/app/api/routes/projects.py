from fastapi import APIRouter, Depends, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.errors import ApiError
from app.api.response import ApiResponse, ok
from app.api.schemas.responses import ProjectFull, ProjectRead
from app.db.db import get_db
from app.db.models.user import User
from app.services import projects as projects_service

projects = APIRouter(prefix="/projects", tags=["projects"])

_MAX_HAR_BYTES = 10 * 1024 * 1024  # NA01: HAR files up to 10 MB


class CreateProject(BaseModel):
    name: str
    domain: str


class PatchProject(BaseModel):
    name: str | None = None
    domain: str | None = None


@projects.get("")
def list_projects(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ApiResponse[list[ProjectRead]]:
    rows = projects_service.list_projects(db, user)
    return ok([ProjectRead.model_validate(p) for p in rows])


@projects.post("")
def create_project(
    body: CreateProject,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ApiResponse[ProjectRead]:
    project = projects_service.create_project(db, user, body.name, body.domain)
    return ok(ProjectRead.model_validate(project), "Project created")


@projects.get("/{project_id}")
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ApiResponse[ProjectFull]:
    project = projects_service.get_owned_project(db, user, project_id)
    return ok(projects_service.build_full(project))


@projects.patch("/{project_id}")
def update_project(
    project_id: int,
    body: PatchProject,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ApiResponse[ProjectRead]:
    project = projects_service.update_project(db, user, project_id, body.name, body.domain)
    return ok(ProjectRead.model_validate(project), "Project updated")


@projects.post("/{project_id}/upload")
async def upload_file(
    project_id: int,
    file: UploadFile,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ApiResponse[None]:
    content = await file.read()
    if len(content) > _MAX_HAR_BYTES:
        raise ApiError("HAR file exceeds the 10 MB limit")
    projects_service.store_har(db, user, project_id, file.filename or "upload.har", content)
    return ok(None, "File uploaded")


@projects.post("/{project_id}/analysis/start")
def start_analysis(
    project_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ApiResponse[None]:
    projects_service.run_analysis(db, user, project_id)
    return ok(None, "Analysis completed")
