"""Events.

Represent something that happened and has to be handled
"""

from dataclasses import dataclass

from backend.still_here.foundation.domain.events import Event


@dataclass
class RegisterDeviceEvent(Event):
    """Register Device Event."""

    uuid: str
    name: str
    last_will: str
    ttl: int
    fire_at: int


@dataclass
class RemoveDeviceEvent(Event):
    """Remove Device Event."""

    uuid: str


@dataclass
class KeepAliveDeviceEvent(Event):
    """Remove Device Event."""

    uuid: str
    fire_at: int
