"""RESTful APIs server."""

import json
import time

from fastapi import APIRouter
from fastapi import FastAPI
from fastapi import Request
from fastapi import Response
from fastapi import status
from fastapi.responses import JSONResponse

from backend.still_here.entrypoints.rest.routers import device
from backend.still_here.entrypoints.rest.schema.shared import ErrorResponseSchema
from backend.still_here.foundation.exceptions import AuthenticationError
from backend.still_here.foundation.exceptions import InvalidArgumentError
from backend.still_here.foundation.exceptions import NotDeletableError
from backend.still_here.foundation.exceptions import NotFoundError
from backend.still_here.foundation.exceptions import NotUpdatableError
from backend.still_here.settings import get_logger
from backend.still_here.settings import init_auth_provider
from backend.still_here.settings import settings

# logger
logger = get_logger()

# authentication provider
auth_provider = init_auth_provider()  # type: ignore[func-returns-value]

# app
app = FastAPI(
    title="HA Still Here Backend",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# routers
base_router = APIRouter(prefix="/api")
base_router.include_router(device.router)
# register routers
app.include_router(base_router)

app.thread_bus_map = {}
# register auth_provider
app.auth_provider = auth_provider


# error handling
@app.exception_handler(Exception)
async def exception_handler(_: Request, exc: Exception) -> JSONResponse:
    """Exception handler.

    Args:
        _ (Request): http Request
        exc (Exception): exception

    Returns:
        JSONResponse: JSON response with error details
    """
    res = JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "details": type(exc).__name__,
        },
    )
    if isinstance(exc, NotFoundError):
        res = JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ErrorResponseSchema(details=str(exc)).model_dump(),
        )
    if isinstance(exc, AuthenticationError):
        res = JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=ErrorResponseSchema(details=str(exc)).model_dump(),
        )
    if isinstance(exc, NotDeletableError | NotUpdatableError):
        res = JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=ErrorResponseSchema(details=str(exc)).model_dump(),
        )
    if isinstance(exc, InvalidArgumentError):
        res = JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ErrorResponseSchema(details=str(exc)).model_dump(),
        )
    return res


# middleware
@app.middleware("http")
async def middleware(request: Request, call_next) -> Response:  # noqa: ANN001
    """Middleware.

    Args:
        request (Request): request to be processed
        call_next (Any): callable to forward the request to the right router

    Returns:
        Response: response to be returned to the user
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.debug(f"Request: {request.url.path} process time: {process_time}")
    return response


# enable remote debugging if DEBUG env variable is set
# to enable debug during development on docker
if settings.debug:
    import debugpy

    logger.debug(json.dumps(settings.model_dump(), indent=2))

    debugpy.listen(("0.0.0.0", 5678))  # noqa S104
    logger.info("debugger listening on container port: 5678")

    if settings.wait_for_debugger_connected:
        logger.info("Waiting for debugger to attach...")
        debugpy.wait_for_client()
        logger.info("Debugger attached. Continuing execution.")
