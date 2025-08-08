"""FastAPI dependencies."""

import threading

from typing import Annotated
from typing import Any
from typing import cast

from fastapi import Depends
from fastapi import Request
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security import OAuth2

from backend.still_here import bootstrap
from backend.still_here.bootstrap import get_device_repository
from backend.still_here.core.service import unit_of_work
from backend.still_here.foundation.exceptions import AuthenticationError
from backend.still_here.messagebus import MessageBus
from backend.still_here.settings import get_logger

# logger
logger = get_logger()


# here we manage a thread safe messagebus to allow declaring, path operations that communicate
# with libraries that does not support await, as simple "def" (these functions will run in a external threadpool)
# this is to prevent multiple concurrent request using the same unit of work at the same time
# changing attributes on the same instance and affecting other requests
# An alternative way will be to pass a fresh new messagebus per request (slower)
# or we can setup a single messagebus and use it in all the request but declaring all
# the path operations with "async def" preventing them from running in different threads
# (faster single request response but requests will queue and start after the previous has been served)
# The external threadpool will simply manage request in different threads that will be anyway awaited
# by the main coroutine, but requests can start processing concurrently when using "def"
def get_bus(request: Request) -> MessageBus:
    """Get internal application messagebus.

    Returns:
        MessageBus: application internal messagebus
    """
    # get application thread bus map
    thread_bus_map = request.app.thread_bus_map
    logger.debug(f"Application registered messagebuses: {request.app.thread_bus_map}")
    thread_id = threading.get_ident()
    # get bus to be used by the thread and register it if not already there
    bus = thread_bus_map.get(thread_id, None)
    if bus is None:
        request.app.thread_bus_map[thread_id] = bootstrap.bootstrap(
            start_orm=False,
            uow=unit_of_work.InMemoryDeviceUnitOfWork(get_device_repository()),
        )
        bus = thread_bus_map.get(thread_id, None)
    return bus


# oauth2 available authorization flows configuration
token_url = "token/"  # noqa: S105
scopes: dict = {}
oauth_scheme = OAuth2(
    flows=OAuthFlowsModel(
        clientCredentials=cast(Any, {"tokenUrl": token_url, "scopes": {}}),
        password=cast(Any, {"tokenUrl": token_url, "scopes": {}}),
    ),
    auto_error=False,
)


def get_authenticated_user(
    request: Request,
    auth_header: Annotated[str | None, Depends(oauth_scheme)] = None,
) -> str:
    """Get authenticated user from headers.

    Args:
        request (Request): HTTP Request to be processed
        auth_header (Annotated[str | None, Depends, optional): Authorization header content.
            Defaults to None.

    Raises:
        AuthenticationError: raised if authentication process fails

    Returns:
        str: authenticated user or ANONYMOUS if auth is not enabled
    """
    username = None
    anon = "ANONYMOUS"

    # auth provider
    auth_provider = request.app.auth_provider
    if auth_provider is not None:
        metadata = {
            "authorization": auth_header,
        }
        auth_data = auth_provider.authenticate(metadata)
        if not auth_data:
            raise AuthenticationError("Authentication failed")
        username = auth_data.get("email")

    return username or anon
