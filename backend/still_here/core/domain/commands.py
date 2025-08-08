"""Commands.

Represent jobs system should perform
"""

from dataclasses import dataclass

from backend.still_here.foundation.domain.commands import Command


@dataclass
class RegisterDeviceCommand(Command):
    """Register Device Command."""

    uuid: str
    name: str
    last_will: str
    ttl: int


@dataclass
class RemoveDeviceCommand(Command):
    """Remove Device Command."""

    uuid: str


@dataclass
class KeepAliveDeviceCommand(Command):
    """Keep Alive Command."""

    uuid: str


@dataclass
class ConsumerCommand(Command):
    """Consumer Command."""

    uuid: str
    consumer_id: str
