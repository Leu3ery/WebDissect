from fastapi import APIRouter, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.errors import ApiError
from app.api.response import fail
from app.config import get_settings
from app.core.logging import get_logger

logger = get_logger("app.api")


def _error_response(status_code: int, message: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content=fail(message).model_dump())


def setup_router(subrouters: list[APIRouter]) -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="WebDissect API", version="1.0.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    api = APIRouter(prefix="/api")
    for router in subrouters:
        api.include_router(router)

    @api.get("/health")
    def health() -> dict:
        return {"status": "ok"}

    app.include_router(api)

    # --- Global error handling (FA06) ------------------------------------
    @app.exception_handler(ApiError)
    async def handle_api_error(request: Request, exc: ApiError):
        logger.info("ApiError on %s: %s", request.url.path, exc.message)
        return _error_response(exc.status_code, exc.message)

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(request: Request, exc: RequestValidationError):
        logger.info("Validation error on %s: %s", request.url.path, exc.errors())
        return _error_response(422, "Invalid request data")

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception):
        logger.exception("Unhandled error on %s", request.url.path)
        return _error_response(500, "Internal server error")

    return app
