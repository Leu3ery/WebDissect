from fastapi import FastAPI, APIRouter, Request
from fastapi.responses import JSONResponse

from app.db import DBError, DBIntegrityError, DBConnectionError


async def _integrity(request: Request, exc: DBIntegrityError):
    return JSONResponse(status_code=409, content={"message": "Constraint violation", "details" : exc.args})

async def _conn(request: Request, exc: DBConnectionError):
    return JSONResponse(status_code=503, content={"message": "Database unavailable", "details" : exc.args})

async def _db(request: Request, exc: DBError):
    return JSONResponse(status_code=500, content={"message": "Database error", "details" : exc.args})


def setup_router(subrouters: list[APIRouter]) -> FastAPI:
    app = FastAPI()

    # Register exception handlers
    app.add_exception_handler(DBIntegrityError, _integrity)
    app.add_exception_handler(DBConnectionError, _conn)
    app.add_exception_handler(DBError, _db)

    api = APIRouter(prefix="/api")

    for router in subrouters:
        api.include_router(router)

    app.include_router(api)
    return app

