"""Message bus.

Handles commands and events routing them to the appropriate handler
"""

from collections.abc import Callable
from typing import Union

from backend.still_here.core.service import unit_of_work
from backend.still_here.foundation.domain import commands
from backend.still_here.foundation.domain import events
from backend.still_here.foundation.exceptions import StillHereBackendBaseError
from backend.still_here.settings import get_logger

logger = get_logger()

Message = Union[commands.Command, events.Event]


class InvalidMessageTypeError(StillHereBackendBaseError):
    """Invalid message type exception.

    Args:
        StillHereBackendBaseError (StillHereBackendBaseError): base exception class
    """


class MessageBus:
    """Internal application message bus.

    dispatches commands and events to the right handler
    """

    def __init__(
        self,
        uow: unit_of_work.AbstractDeviceUnitOfWork,
        event_handlers: dict[type[events.Event], list[Callable]],
        command_handlers: dict[type[commands.Command], Callable],
    ):
        """Inits MessageBus.

        Args:
            uow (unit_of_work.AbstractDeviceUnitOfWork): unit of work
            event_handlers (Dict[Type[events.Event], List[Callable]]):
                event handlers map
            command_handlers (Dict[Type[commands.Command], Callable]):
                command handlers map
        """
        self.uow = uow
        self.event_handlers = event_handlers
        self.command_handlers = command_handlers

    def handle(self, message: Message):
        """Handle message dispatching to the right handler.

        it also keeps the queue for messages to be handled

        Args:
            message (Message): command or event

        Raises:
            InvalidMessageTypeError: Invalid message type exception in case of
                message has not a valid type
        """
        self.queue = [message]
        while self.queue:
            message = self.queue.pop(0)
            if isinstance(message, events.Event):
                self._handle_event(message)
            elif isinstance(message, commands.Command):
                self._handle_command(message)
            else:
                raise InvalidMessageTypeError(
                    f"{message} is not an Event or Command",
                )

    def _handle_event(self, event: events.Event):
        for handler in self.event_handlers[type(event)]:
            try:
                logger.debug(f"handling event {event} with handler {handler}")
                handler(event)
                # collect new events
                self.queue.extend(self.uow.collect_new_events())
            except Exception:
                logger.exception(f"Exception handling event {event}")
                # event exceptions must be logged but recovery will
                # happen at a later point, manually
                # the execution flow must not be interrupted
                # events are threated like async processing
                continue

    def _handle_command(self, command: commands.Command):
        logger.debug(f"handling command {command}")
        try:
            handler = self.command_handlers[type(command)]
            handler(command)
            # collect new events
            self.queue.extend(self.uow.collect_new_events())
        except Exception:
            logger.exception(f"Exception handling command {command}")
            raise
