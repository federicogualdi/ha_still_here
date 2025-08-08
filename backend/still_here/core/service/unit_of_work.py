"""Unit of Work.

abstraction around data integrity, represents an atomic update,
makes repositories available and tracks events on retrieved aggregates.
"""

from typing import Optional

from backend.still_here.core import repository
from backend.still_here.core.domain.model import Device
from backend.still_here.core.repository import AbstractDeviceRepository
from backend.still_here.core.repository import InMemoryDeviceRepository
from backend.still_here.foundation.service.unit_of_work import AbstractUnitOfWork


class AbstractDeviceUnitOfWork(AbstractUnitOfWork):
    """Abstract class to define Device unit of work behavior.

    Args:
        AbstractUnitOfWork (AbstractUnitOfWork): Base abstract unit of work

    Raises:
        NotImplementedError: not implemented error for abstract methods
    """

    def __init__(self):
        """Abstract Unit of Work Constructor."""
        self._devices: Optional[repository.AbstractDeviceRepository] = None

    def collect_new_events(self):
        """Collect events from all visited repository items."""
        if self.devices:
            for device in self.devices.seen:
                while device.events:
                    yield device.events.pop(0)

    @property
    def devices(self) -> repository.AbstractDeviceRepository:
        """Ensure devices is initialized before use."""
        if self._devices is None:
            raise RuntimeError("Devices repository has not been initialized yet.")
        return self._devices

    @devices.setter
    def devices(self, value: repository.AbstractDeviceRepository):
        self._devices = value


class InMemoryDeviceUnitOfWork(AbstractDeviceUnitOfWork):
    """Concrete Unit of Work for in-memory device repository."""

    def __init__(self, repository: AbstractDeviceRepository = InMemoryDeviceRepository()):
        """Unit of work initialization with sessionmaker.

        Args:
            repository: AbstractDeviceRepository
        """
        super().__init__()
        self._repository = repository
        self._backup: dict[str, Device] = {}

    def __enter__(self) -> "InMemoryDeviceUnitOfWork":
        """Context manager entering."""
        self._backup = self._repository.get_all_by_uuid().copy()
        self.devices = self._repository
        return self

    def __exit__(self, *args):
        """Exit from context manager."""
        super().__exit__(*args)

    def _commit(self):
        """Commit work."""

    def rollback(self):
        """Rollback work."""
        if self._backup is None:
            return

        # Restore full state
        devices = self._backup.copy().values()
        self._repository.remove_all()
        for device in devices:
            self._repository.add(device)
