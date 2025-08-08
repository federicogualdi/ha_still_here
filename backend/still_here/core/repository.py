"""core repository.

abstraction around persistent storage, each aggregate has its own repository
"""

import abc

from collections import defaultdict

from backend.still_here.core.domain import model
from backend.still_here.core.domain.model import Device


class AbstractDeviceRepository(abc.ABC):
    """Abstract repository.

    From this, concrete repository for Device must be implemented

    Args:
        abc (abc.ABC): Abstract class
    """

    def __init__(self):
        """Initialize repository."""
        # track seen elements
        self.seen: set[model.Device] = set()

    def get(self, uuid: str) -> model.Device | None:
        """Get Device object by uuid.

        Args:
            uuid (str): Device unique identifier

        Returns:
            model.Device | None: Device model instance or None
        """
        device = self._get(uuid)
        if device:
            # track seen element
            self.seen.add(device)
        return device

    def get_all_by_uuid(self) -> dict[str, Device]:
        """Get Devices.

        Returns:
            dict[str, Device]: Devices dict or empty dict
        """
        devices_map = self._get_all_by_uuid()
        if devices_map:
            # track seen element
            self.seen.update(devices_map.values())
        return devices_map

    def get_fire_at_between(self, start: int, end: int) -> list[Device]:
        """Return all devices scheduled to fire between the given timestamps (inclusive).

        Args:
            start (int): Start of the interval (included), as a UNIX timestamp in seconds (UTC).
            end (int): End of the interval (included), as a UNIX timestamp in seconds (UTC).

        Returns:
            list[Device]: List of devices scheduled to fire within the given interval.
        """
        devices = self._get_fire_at_between(start, end)
        if devices:
            # track seen element
            self.seen.update(devices)
        return devices

    def add(self, device: model.Device):
        """Add Device object to session.

        Args:
            device (model.Device): Device model instance
        """
        self._add(device)
        # track seen element
        self.seen.add(device)

    def update(self, uuid: str, **fields):
        """Remove Device object to session.

        Args:
            uuid (str): Device unique identifier
            fields: Fields to update
        """
        device = self.get(uuid)
        if device:
            self._update(uuid, **fields)
            # track seen element
            self.seen.add(device)

    def remove(self, uuid: str):
        """Remove Device object to session.

        Args:
            uuid (str): Device unique identifier
        """
        device = self.get(uuid)
        if device:
            self._remove(uuid)
            # track seen element
            self.seen.add(device)

    def remove_all(self):
        """Remove all Device object to session."""
        devices = self.get_all_by_uuid()
        if devices:
            self._remove_all()
            # track seen element
            self.seen.update(devices.values())

    @abc.abstractmethod
    def _add(self, ex: model.Device):
        raise NotImplementedError

    @abc.abstractmethod
    def _get(self, uuid: str) -> model.Device | None:
        raise NotImplementedError

    @abc.abstractmethod
    def _get_all_by_uuid(self) -> dict[str, Device]:
        raise NotImplementedError

    @abc.abstractmethod
    def _get_fire_at_between(self, start: int, end: int) -> list[model.Device]:
        raise NotImplementedError

    @abc.abstractmethod
    def _update(self, uuid: str, **fields) -> model.Device | None:
        raise NotImplementedError

    @abc.abstractmethod
    def _remove(self, uuid: str) -> model.Device | None:
        raise NotImplementedError

    @abc.abstractmethod
    def _remove_all(self) -> None:
        raise NotImplementedError


class InMemoryDeviceRepository(AbstractDeviceRepository):
    """In Memory repository for Device.

    Args:
        AbstractRepository (AbstractDeviceRepository): abstract class defining
            repository behavior
    """

    def __init__(self):
        """Initialize repository."""
        super().__init__()
        self.by_uuid: dict[str, Device] = {}
        self.by_fire_at: defaultdict[int, set[str]] = defaultdict(set)

    def _add(self, device: model.Device) -> None:
        """Add a device to the repository and index it."""
        self.by_uuid[device.uuid] = device
        self.by_fire_at[device.fire_at].add(device.uuid)

    def _get(self, uuid: str) -> model.Device | None:
        """Retrieve a device by UUID."""
        return self.by_uuid.get(uuid)

    def _get_all_by_uuid(self) -> dict[str, Device]:
        """Retrieve all devices."""
        return self.by_uuid

    def _get_fire_at_between(self, start: int, end: int) -> list[Device]:
        """Return devices scheduled in [start, end] inclusive."""
        devices = []
        for ts in range(start, end + 1):  # it's inclusive
            for uuid in self.by_fire_at.get(ts, set()):
                device = self._get(uuid)
                if device:
                    devices.append(device)
            self.by_fire_at.pop(ts, None)
        return devices

    def _update(self, uuid: str, **fields) -> None:
        """Update a device's attributes and re-index if necessary."""
        device = self.by_uuid.get(uuid)
        if not device:
            return

        old_fire_at = device.fire_at

        for key, value in fields.items():
            setattr(device, key, value)

        # Re-index fire_at if changed
        if "fire_at" in fields and fields["fire_at"] != old_fire_at:
            self.by_fire_at[old_fire_at].discard(uuid)
            if not self.by_fire_at[old_fire_at]:
                del self.by_fire_at[old_fire_at]
            self.by_fire_at[fields["fire_at"]].add(uuid)

    def _remove(self, uuid: str) -> None:
        """Delete a device and clean up indexes."""
        device = self.by_uuid.pop(uuid, None)
        if device:
            self.by_fire_at[device.fire_at].discard(uuid)
            if not self.by_fire_at[device.fire_at]:
                del self.by_fire_at[device.fire_at]

    def _remove_all(self) -> None:
        """Delete all devices and clean up indexes."""
        self.by_uuid.clear()
        self.by_fire_at.clear()
