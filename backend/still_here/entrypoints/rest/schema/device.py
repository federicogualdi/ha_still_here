"""Device API Schema."""

from backend.still_here.entrypoints.rest.schema.shared import BaseSchema


class RegisterDevice(BaseSchema):
    """Register Device schema."""

    uuid: str
    name: str
    last_will: str
    ttl: int
