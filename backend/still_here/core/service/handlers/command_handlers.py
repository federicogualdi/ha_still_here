"""Command Handlers.

receive commands and perform the required action
"""

from datetime import datetime

from backend.still_here.core.domain import commands
from backend.still_here.core.domain import model
from backend.still_here.core.service import unit_of_work
from backend.still_here.foundation.exceptions import NotFoundError
from backend.still_here.foundation.utils import get_utc_tz_aware_datetime
from backend.still_here.settings import get_logger

logger = get_logger()


def register_device(
    cmd: commands.RegisterDeviceCommand,
    uow: unit_of_work.AbstractDeviceUnitOfWork,
):
    """Register Device handler for Register Device command.

    Args:
        cmd (commands.RegisterDeviceCommand): command triggering this handler
        uow (unit_of_work.AbstractDeviceUnitOfWork): unit of work
    """
    with uow:
        device = model.Device(
            uuid=cmd.uuid,
            name=cmd.name,
            last_will=cmd.last_will,
            ttl=cmd.ttl,
            created_at=get_utc_tz_aware_datetime(datetime.now()),
        )
        # save data
        uow.devices.add(device)
        device.generate_event_register_device()
        # commit
        uow.commit()


def remove_device(
    cmd: commands.RemoveDeviceCommand,
    uow: unit_of_work.AbstractDeviceUnitOfWork,
):
    """Remove Device handler for Remove Device command.

    Args:
        cmd (commands.RegisterDeviceCommand): command triggering this handler
        uow (unit_of_work.AbstractDeviceUnitOfWork): unit of work
    """
    with uow:
        device = uow.devices.get(cmd.uuid)

        if not device:
            raise NotFoundError(f"device {cmd.uuid} not found")

        uow.devices.remove(device.uuid)
        device.generate_event_remove_device()
        # commit
        uow.commit()


def keep_alive_device(
    cmd: commands.KeepAliveDeviceCommand,
    uow: unit_of_work.AbstractDeviceUnitOfWork,
):
    """Keep Alive Device handler for Keep Alive Device command.

    Args:
        cmd (commands.KeepAliveDeviceCommand): command triggering this handler
        uow (unit_of_work.AbstractDeviceUnitOfWork): unit of work
    """
    with uow:
        device = uow.devices.get(cmd.uuid)

        if not device:
            raise NotFoundError(f"device {cmd.uuid} not found")

        params = {"fire_at": int(get_utc_tz_aware_datetime(datetime.now()).timestamp()) + device.ttl}
        uow.devices.update(device.uuid, **params)
        device.generate_event_keep_alive_device()
        # commit
        uow.commit()
