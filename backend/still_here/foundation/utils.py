"""Utility functions."""

import uuid

from datetime import UTC
from datetime import datetime


def generate_unique_identifier() -> str:
    """Generates an unique identifier.

    Returns:
        str: unique string identifier
    """
    return str(uuid.uuid4())


def is_uuid(uuid_str: str) -> bool:
    """Checks if provided string is a valid UUID.

    Args:
        uuid_str (str): uuid string

    Returns:
        bool: valid uuid or not
    """
    valid = True
    try:
        uuid.UUID(uuid_str)
    except ValueError:
        valid = False

    return valid


def get_utc_tz_aware_datetime(dt: datetime) -> datetime:
    """Get UTC Timezone Aware from possible naive datetime.

    Args:
        dt (datetime): datetime with or without tzinfo

    Returns:
        datetime: UTC Timezone aware datetime
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt
