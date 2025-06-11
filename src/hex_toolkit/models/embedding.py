"""Models for embedding-related API responses."""

from enum import Enum
from typing import Any

from pydantic import Field

from hex_toolkit.models.base import HexBaseModel


class ThemeType(str, Enum):
    """Theme options for embedded apps."""

    LIGHT = "light"
    DARK = "dark"


class DisplayOptions(HexBaseModel):
    """Display options for embedded apps."""

    theme: ThemeType | None = None
    no_embed_base_padding: bool | None = Field(None, alias="noEmbedBasePadding")
    no_embed_outline: bool | None = Field(None, alias="noEmbedOutline")
    no_embed_footer: bool | None = Field(None, alias="noEmbedFooter")


class EmbeddingRequest(HexBaseModel):
    """Request body for creating an embedded URL."""

    hex_user_attributes: dict[str, str] | None = Field(
        None,
        alias="hexUserAttributes",
        description="Map of attributes to populate hex_user_attributes",
    )
    scope: list[str] | None = Field(
        None, description="Additional permissions (EXPORT_PDF, EXPORT_CSV)"
    )
    input_parameters: dict[str, Any] | None = Field(
        None, alias="inputParameters", description="Default values for input states"
    )
    expires_in: float | None = Field(
        None,
        alias="expiresIn",
        description="Expiration time in milliseconds (max 300000)",
        ge=0,
        le=300000,
    )
    display_options: DisplayOptions | None = Field(
        None,
        alias="displayOptions",
        description="Customize the display of the embedded app",
    )
    test_mode: bool | None = Field(
        None,
        alias="testMode",
        description="Run in test mode without counting towards limits",
    )


class EmbeddingResponse(HexBaseModel):
    """Response from creating an embedded URL."""

    url: str = Field(..., description="The presigned URL for embedding")
