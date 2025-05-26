"""Base models for the Hex API SDK."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class HexBaseModel(BaseModel):
    """Base model with common configuration."""

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        arbitrary_types_allowed=True,
        str_strip_whitespace=True,
    )


class PaginationInfo(HexBaseModel):
    """Pagination information for list responses."""

    after: Optional[str] = Field(None, description="Cursor for next page")
    before: Optional[str] = Field(None, description="Cursor for previous page")


class TraceInfo(HexBaseModel):
    """Trace information for debugging."""

    trace_id: Optional[str] = Field(None, alias="traceId")


class ErrorResponse(TraceInfo):
    """Error response from the API."""

    reason: str = Field(..., description="Error reason")
    details: Optional[str] = Field(None, description="Additional error details")
