"""App bootstrapping.

Main components initialization and dependency injection management
"""

import inspect

from collections.abc import Callable
from typing import Any

from backend.still_here import messagebus
from backend.still_here.core.domain import commands
from backend.still_here.core.domain import events
from backend.still_here.core.repository import AbstractDeviceRepository
from backend.still_here.core.repository import InMemoryDeviceRepository
from backend.still_here.core.service import unit_of_work
from backend.still_here.core.service.handlers import command_handlers
from backend.still_here.core.service.handlers import event_handlers
from backend.still_here.foundation.domain import commands as commands_common
from backend.still_here.foundation.domain import events as events_common

# event handlers mapping
EVENT_HANDLERS: dict[type[events_common.Event], list[Callable]] = {
    events.RegisterDeviceEvent: [event_handlers.register_device_event],
    events.RemoveDeviceEvent: [event_handlers.remove_device_event],
    events.KeepAliveDeviceEvent: [event_handlers.keep_alive_device_event],
}

# command handlers mapping
COMMAND_HANDLERS: dict[type[commands_common.Command], Callable] = {
    commands.RegisterDeviceCommand: command_handlers.register_device,
    commands.ConsumerCommand: command_handlers.remove_device,
    commands.KeepAliveDeviceCommand: command_handlers.keep_alive_device,
}

_device_repository = InMemoryDeviceRepository()


def get_device_repository() -> AbstractDeviceRepository:
    """Return the shared in-memory device repository instance.

    This ensures all unit of work instances use the same in-memory store.
    """
    return _device_repository


def bootstrap(
    start_orm: bool = True,  # noqa: ARG001
    uow: unit_of_work.AbstractDeviceUnitOfWork = unit_of_work.InMemoryDeviceUnitOfWork(get_device_repository()),
) -> messagebus.MessageBus:
    """Application bootstrapping with dependencies injection management.

    Args:
        start_orm (bool): start orm mappers
            Defaults to True.
        uow (unit_of_work.AbstractDeviceUnitOfWork): core unit of work.
            Defaults to unit_of_work.InMemoryDeviceUnitOfWork.

    Returns:
        messagebus.MessageBus: internal messagebus (dispatcher)
    """
    # define injectable dependencies
    dependencies = {"uow": uow}

    injected_event_handlers = {
        event_type: [_inject_dependencies(handler, dependencies) for handler in event_handlers]
        for event_type, event_handlers in EVENT_HANDLERS.items()
    }

    injected_command_handlers = {
        command_type: _inject_dependencies(handler, dependencies) for command_type, handler in COMMAND_HANDLERS.items()
    }

    return messagebus.MessageBus(
        uow=uow,
        event_handlers=injected_event_handlers,
        command_handlers=injected_command_handlers,
    )


def _inject_dependencies(handler: Callable, dependencies: dict[str, Any]):  # noqa ANN202
    """Inject dependencies using partials.

    Args:
        handler (Callable): handler function
        dependencies (dict): dependencies dictionary

    Returns:
        Callable: lambda function executing a partial with injected dependencies
    """
    params = inspect.signature(handler).parameters
    deps = {name: dependency for name, dependency in dependencies.items() if name in params}
    return lambda message: handler(message, **deps)
