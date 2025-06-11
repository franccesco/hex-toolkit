"""Base models for the Hex API SDK."""


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

    after: str | None = Field(None, description="Cursor for next page")
    before: str | None = Field(None, description="Cursor for previous page")


class TraceInfo(HexBaseModel):
    """Trace information for debugging."""

    trace_id: str | None = Field(None, alias="traceId")


class ErrorResponse(TraceInfo):
    """Error response from the API."""

    reason: str = Field(..., description="Error reason")
    details: str | None = Field(None, description="Additional error details")
