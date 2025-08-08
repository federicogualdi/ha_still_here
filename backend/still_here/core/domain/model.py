"""Domain Models.

In this file are defined all the domain related relevant entities,
aggregates and value objects.

aggregate: cluster of associated objects that is treated as a unit for
the purpose of data changes. (defines consistency boundary).

value object: immutable domain object entirely defined by its attributes.

entity: domain object whose attributes may change,
but with a recognizable identity over time.
"""

from backend.still_here.core.domain import events
from backend.still_here.foundation.domain.events import Event
from backend.still_here.settings import get_logger

logger = get_logger()


class Device:
    """core business model aggregate."""

    def __init__(  # noqa: PLR0913
        self,
        uuid: str,
        name: str,
        last_will: str,
        ttl: int,
        created_at: int,
        consumer_id: str | None = None,
        consumed: bool = False,
        version_number: int = 0,
    ) -> None:
        """Initialize entity."""
        self.uuid = uuid
        self.name = name
        self.last_will = last_will
        self.ttl = ttl
        self.created_at = created_at
        self.fire_at = created_at + self.ttl
        self.consumer_id = consumer_id
        self.consumed = consumed
        # tracks generated events related to this aggregate
        self.events: list[Event] = []
        # version number for optimistic concurrency control
        self.version_number = version_number

    def generate_event_register_device(self):
        """Generate event in response to command execution."""
        # generate event
        ev = events.RegisterDeviceEvent(
            uuid=self.uuid,
            name=self.name,
            last_will=self.last_will,
            ttl=self.ttl,
            fire_at=self.fire_at,
        )
        self.events.append(ev)

    def generate_event_remove_device(self):
        """Generate event in response to command execution."""
        # generate event
        ev = events.RemoveDeviceEvent(uuid=self.uuid)
        self.events.append(ev)

    def generate_event_keep_alive_device(self):
        """Generate event in response to command execution."""
        # generate event
        ev = events.KeepAliveDeviceEvent(
            uuid=self.uuid,
            fire_at=self.fire_at,
        )
        self.events.append(ev)

    def consume(self, consumer_id: str):
        """Register consumer on message.

        Args:
            consumer_id (str): consumer id
        """
        if self.consumed:
            logger.warning("consuming already consumed message!")
        self.version_number += 1
        self.consumed = True
        self.consumer_id = consumer_id

    def __repr__(self) -> str:
        """String representation."""
        return f"<Device {self.uuid}, {self.name}>"

    def __eq__(self, obj: object) -> bool:
        """Equals."""
        if not isinstance(obj, Device):
            return False
        return obj.uuid == self.uuid

    def __hash__(self) -> int:
        """Hash."""
        return hash(self.uuid)
