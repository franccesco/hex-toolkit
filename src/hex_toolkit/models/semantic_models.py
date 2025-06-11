"""Models for semantic model-related API responses."""

from typing import Any

from pydantic import Field

from hex_toolkit.models.base import HexBaseModel


class SemanticModelIngestRequest(HexBaseModel):
    """Request body for ingesting a semantic model."""

    verbose: bool = Field(
        True, description="Whether to respond with detail on synced components"
    )
    debug: bool = Field(
        False, description="Whether to include additional debug information"
    )
    dry_run: bool = Field(
        False,
        alias="dryRun",
        description="If enabled, the sync will not write to the database",
    )


class MetricflowModelSchemas(HexBaseModel):
    """Metricflow model schemas information."""

    # This is defined as a generic dict in the OpenAPI spec
    # It's a Record<string, Record<string, HexSLTypes.DataType>>
    pass


class SemanticModelDebugInfo(HexBaseModel):
    """Debug information for semantic model sync."""

    metricflow_model_schemas: MetricflowModelSchemas | None = Field(
        None, alias="metricflowModelSchemas"
    )


class SemanticModelsSyncResponse(HexBaseModel):
    """Response from semantic model sync."""

    trace_id: str = Field(..., alias="traceId")
    warnings: list[str] = []
    skipped: dict[str, Any] = {}
    debug: SemanticModelDebugInfo | None = None
