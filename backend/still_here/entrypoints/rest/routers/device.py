"""Device APIs."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter
from fastapi import Path
from fastapi import status

from backend.still_here.core.domain import commands
from backend.still_here.entrypoints.rest.schema.device import RegisterDevice
from backend.still_here.entrypoints.rest.schema.shared import AuthUser
from backend.still_here.entrypoints.rest.schema.shared import Bus
from backend.still_here.entrypoints.rest.schema.shared import ErrorResponseSchema
from backend.still_here.entrypoints.rest.schema.shared import ObjectCreatedResponse
from backend.still_here.entrypoints.rest.schema.shared import ObjectRemovedResponse
from backend.still_here.entrypoints.rest.schema.shared import ObjectUpdatedResponse
from backend.still_here.foundation import utils
from backend.still_here.foundation.exceptions import InvalidArgumentError
from backend.still_here.settings import get_logger

# logger
logger = get_logger()

# router definition
router = APIRouter(prefix="/device", tags=["Device"])

# annotated items
DeviceUUID = Annotated[UUID, Path(..., description="Device UUID")]


@router.post(
    "/",
    summary="Register a new Device",
    status_code=status.HTTP_201_CREATED,
    response_model=ObjectCreatedResponse,
    responses={
        status.HTTP_201_CREATED: {"description": "Returns register Device uuid"},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponseSchema, "description": "Invalid input data"},
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponseSchema, "description": "Authentication Failed"},
    },
)
def register_device(bus: Bus, auth_user: AuthUser, request: RegisterDevice) -> ObjectCreatedResponse:
    """Register a new device in the system.

    Args:
        bus (Bus): Command bus to dispatch domain logic.
        auth_user (AuthUser): Authenticated user making the request.
        request (RegisterDevice): Data required to register the device (UUID, name, last_will, TTL).

    Returns:
        ObjectCreatedResponse: Response containing the UUID of the newly registered device.
    """
    if not utils.is_uuid(request.uuid):
        raise InvalidArgumentError("UUID malformed")

    cmd = commands.RegisterDeviceCommand(
        uuid=request.uuid,
        name=request.name,
        last_will=request.last_will,
        ttl=request.ttl,
    )
    bus.handle(cmd)
    logger.info(f"New Device registered by: {auth_user}")
    return ObjectCreatedResponse(uuid=cmd.uuid)


@router.delete(
    "/{uuid}",
    summary="Remove a Device",
    status_code=status.HTTP_200_OK,
    response_model=ObjectRemovedResponse,
    responses={
        status.HTTP_200_OK: {"description": "UUID of the removed device"},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponseSchema, "description": "Invalid input data"},
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponseSchema, "description": "Authentication Failed"},
    },
)
def remove_device(bus: Bus, auth_user: AuthUser, uuid: str) -> ObjectRemovedResponse:
    """Delete a device from the system.

    Args:
        bus (Bus): Command bus to dispatch domain logic.
        auth_user (AuthUser): Authenticated user making the request.
        uuid (str): UUID of the device to remove.

    Returns:
        ObjectRemovedResponse: Response containing the UUID of the removed device.
    """
    if not utils.is_uuid(uuid):
        raise InvalidArgumentError("UUID malformed")

    cmd = commands.RemoveDeviceCommand(uuid=uuid)
    bus.handle(cmd)
    logger.info(f"Device removed by: {auth_user}")
    return ObjectRemovedResponse(uuid=cmd.uuid)


@router.post(
    "/{uuid}/keep-alive",
    summary="Keep a device alive",
    status_code=status.HTTP_200_OK,
    response_model=ObjectUpdatedResponse,
    responses={
        status.HTTP_201_CREATED: {"description": "Device keep-alive acknowledged"},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponseSchema, "description": "Invalid input data"},
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponseSchema, "description": "Authentication failed"},
    },
)
def keep_alive_device(bus: Bus, auth_user: AuthUser, uuid: str) -> ObjectUpdatedResponse:
    """Refresh the keep-alive timer of a device.

    This will update the device's TTL and postpone the execution of its associated last-will action.

    Args:
        bus (Bus): Command bus to dispatch domain logic.
        auth_user (AuthUser): Authenticated user making the request.
        uuid (UUID): UUID of the device.

    Returns:
        ObjectUpdatedResponse: Response containing the UUID of the updated device.
    """
    if not utils.is_uuid(uuid):
        raise InvalidArgumentError("UUID malformed")

    cmd = commands.KeepAliveDeviceCommand(
        uuid=uuid,
    )
    bus.handle(cmd)
    logger.info(f"New Device registered by: {auth_user}")
    return ObjectUpdatedResponse(uuid=cmd.uuid)
