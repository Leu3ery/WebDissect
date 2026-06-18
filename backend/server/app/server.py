from app.api.router import setup_router
from app.api.routes.projects import projects
from app.api.routes.tools import tools

app = setup_router([projects, tools])