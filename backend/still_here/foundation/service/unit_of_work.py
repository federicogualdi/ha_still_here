"""Abstract Unit of Work.

abstraction around data integrity, represents an atomic update,
makes repositories available and tracks events on retrieved aggregates.
"""

import abc


class AbstractUnitOfWork(abc.ABC):
    """Abstract class to define unit of work behavior.

    Args:
        abc (abc.ABC): abstract class

    Raises:
        NotImplementedError: not implemented error for abstract methods
    """

    def __enter__(self) -> "AbstractUnitOfWork":
        """Enter."""
        return self

    def __exit__(self, *args):
        """Exit."""
        self.rollback()

    def commit(self):
        """Commit transaction."""
        self._commit()

    def collect_new_events(self):
        """Collect events from all visited repository items."""
        raise NotImplementedError

    @abc.abstractmethod
    def _commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self):
        """Rollback transaction."""
        raise NotImplementedError
