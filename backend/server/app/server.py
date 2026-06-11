from app.api.router import setup_router
from app.api.routes.auth import auth
from app.api.routes.projects import projects
from app.core.logging import setup_logging
from app.db.db import init_db

setup_logging()
init_db()

app = setup_router([auth, projects])
