from fastapi import FastAPI, APIRouter


def setup_router(subrouters: list[APIRouter]) -> FastAPI:
    app = FastAPI()
    api = APIRouter(prefix="/api")

    for router in subrouters:
        api.include_router(router)

    app.include_router(api)
    return app

