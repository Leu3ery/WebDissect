from fastapi import APIRouter, Depends, Query, UploadFile, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.errors import ApiError
from app.api.rate_limit import scan_limiter
from app.api.response import ApiResponse, ok
from app.api.schemas.responses import ProjectFull, ProjectRead
from app.core.security import decode_access_token
from app.db.db import SessionLocal, get_db
from app.db.models.project import Project
from app.db.models.user import User
from app.services import analysis as analysis_service
from app.services import projects as projects_service
from app.services.analysis_hub import hub

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
async def start_analysis(
    project_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ApiResponse[None]:
    """Kick off the passive analysis in the background; progress streams over WS."""
    projects_service.get_owned_project(db, user, project_id)  # ownership check
    analysis_service.schedule(analysis_service.run_passive, project_id)
    return ok(None, "Analysis started")


@projects.post("/{project_id}/scan/ports", dependencies=[Depends(scan_limiter)])
async def scan_ports(
    project_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ApiResponse[None]:
    """Opt-in TCP port scan + banner grab against the target."""
    projects_service.get_owned_project(db, user, project_id)
    analysis_service.schedule(analysis_service.run_port_scan, project_id)
    return ok(None, "Port scan started")


@projects.post("/{project_id}/scan/paths", dependencies=[Depends(scan_limiter)])
async def scan_paths(
    project_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ApiResponse[None]:
    """Opt-in path/directory enumeration against the target."""
    projects_service.get_owned_project(db, user, project_id)
    analysis_service.schedule(analysis_service.run_path_scan, project_id)
    return ok(None, "Path scan started")


@projects.websocket("/{project_id}/analysis/ws")
async def analysis_ws(
    websocket: WebSocket,
    project_id: int,
    token: str = Query(default=""),
) -> None:
    """Stream live analysis progress. Auth via ?token= since browsers can't set
    WebSocket headers."""
    user_id = decode_access_token(token)
    if user_id is None or not _owns_project(user_id, project_id):
        await websocket.close(code=4401)
        return

    await websocket.accept()
    hub.bind_loop_from_running()
    queue = hub.subscribe(project_id)
    try:
        await websocket.send_json({"type": "snapshot", **hub.snapshot(project_id)})
        while True:
            event = await queue.get()
            await websocket.send_json(event)
    except WebSocketDisconnect:
        pass
    finally:
        hub.unsubscribe(project_id, queue)


def _owns_project(user_id: int, project_id: int) -> bool:
    db = SessionLocal()
    try:
        return (
            db.query(Project)
            .filter(Project.id == project_id, Project.user_id == user_id)
            .first()
            is not None
        )
    finally:
        db.close()
