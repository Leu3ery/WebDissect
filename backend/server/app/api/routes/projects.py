from fastapi import APIRouter

projects = APIRouter(prefix="/projects")


@projects.get("/{project_id}")
def get_project(project_id: int):
    pass


@projects.post("")
def create_project():
    pass


@projects.patch("/{project_id}")
def update_project(project_id: int):
    pass



@projects.post("/{project_id}/upload")
def upload_file(project_id: int):
    pass



@projects.post("/{project_id}/analysis/start")
def start_analysis(project_id: int):
    pass

