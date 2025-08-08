"""Event Handlers.

receive events and perform the required action
"""

from backend.still_here.core.domain import events
from backend.still_here.settings import get_logger

logger = get_logger()


def register_device_event(
    event: events.RegisterDeviceEvent,
):
    """Register Device Event.

    Args:
        event (events.RegisterDeviceEvent): event generated internally.
    """
    # this is an example of an internal event
    logger.info(f"register_device command executed and generated this event {event}")


def remove_device_event(
    event: events.RemoveDeviceEvent,
):
    """Remove Device Event.

    Args:
        event (events.RemoveDeviceEvent): event generated internally.
    """
    # this is an example of an internal event
    logger.info(f"remove_device command executed and generated this event {event}")


def keep_alive_device_event(
    event: events.KeepAliveDeviceEvent,
):
    """Keep Alive Device Event.

    Args:
        event (events.KeepAliveDeviceEvent): event generated internally.
    """
    # this is an example of an internal event
    logger.info(f"keep_alive_device command executed and generated this event {event}")
