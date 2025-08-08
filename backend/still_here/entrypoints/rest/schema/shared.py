"""Shared schemas."""

from typing import Annotated

from fastapi import Depends
from fastapi import Query
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field
from pydantic.alias_generators import to_camel

from backend.still_here.entrypoints.rest.dependencies import get_authenticated_user
from backend.still_here.entrypoints.rest.dependencies import get_bus
from backend.still_here.messagebus import MessageBus


class BaseSchema(BaseModel):
    """Base model used in all the schemas."""

    model_config = ConfigDict(
        # Allow the usage of the snake case of the fields instead of their aliases
        populate_by_name=True,
        # When serializing/deserializing, convert to and from camel case
        alias_generator=to_camel,
        extra="forbid",
    )


# Annotated types
Bus = Annotated[MessageBus, Depends(get_bus)]
AuthUser = Annotated[str, Depends(get_authenticated_user)]
Page = Query(1, ge=1, description="Page number to select")
Size = Query(10, ge=1, description="Maximum number of items to retrieve per page")


class PaginationRequest(BaseSchema):
    """Pagination request schema."""

    page: int
    page_size: int


class PaginationMetadata(BaseSchema):
    """Pagination metadata schema."""

    current_page: int = Field(..., description="Currently selected page")
    page_size: int = Field(..., description="Desired page size limit")
    size: int = Field(..., description="Number of actual items in the current page")
    total: int = Field(0, description="Total number of items available")
    total_pages: int = Field(0, description="Total number of pages available")


class ObjectCreatedResponse(BaseModel):
    """Object created response schema."""

    uuid: str


class ObjectUpdatedResponse(BaseModel):
    """Object updated response schema."""

    uuid: str


class ObjectRemovedResponse(BaseModel):
    """Object deleted response schema."""

    uuid: str


class ErrorResponseSchema(BaseModel):
    """Error response schema."""

    details: str


def _pagination_params(page: int = Page, page_size: int = Size) -> PaginationRequest:
    """Return an object representing the pagination request."""
    return PaginationRequest(page=page, page_size=page_size)


PaginationType = Annotated[PaginationRequest, Depends(_pagination_params)]


def paginate(page: int, page_size: int, size: int, total: int = 0) -> PaginationMetadata:
    """Build pagination metadata."""
    return PaginationMetadata(
        current_page=page,
        page_size=page_size,
        size=size,
        total=total,
        total_pages=(total + page_size - 1) // page_size if total else 0,
    )
