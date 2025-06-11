"""Embedding resource for the Hex API SDK."""

from typing import Any
from uuid import UUID

from hex_toolkit.models.embedding import (
    DisplayOptions,
    EmbeddingRequest,
    EmbeddingResponse,
)
from hex_toolkit.resources.base import BaseResource


class EmbeddingResource(BaseResource):
    """Resource for embedding-related API endpoints."""

    def create_presigned_url(
        self,
        project_id: str | UUID,
        hex_user_attributes: dict[str, str] | None = None,
        scope: list[str] | None = None,
        input_parameters: dict[str, Any] | None = None,
        expires_in: float | None = None,
        display_options: DisplayOptions | None = None,
        test_mode: bool = False,
    ) -> EmbeddingResponse:
        """Create an embedded URL for a project.

        Args:
            project_id: Unique ID for the project
            hex_user_attributes: Map of attributes to populate hex_user_attributes
            scope: Additional permissions (EXPORT_PDF, EXPORT_CSV)
            input_parameters: Default values for input states
            expires_in: Expiration time in milliseconds (max 300000)
            display_options: Customize the display of the embedded app
            test_mode: Run in test mode without counting towards limits

        Returns:
            EmbeddingResponse with the presigned URL
        """
        request = EmbeddingRequest(
            hex_user_attributes=hex_user_attributes,
            scope=scope,
            input_parameters=input_parameters,
            expires_in=expires_in,
            display_options=display_options,
            test_mode=test_mode,
        )

        data = self._post(
            f"/v1/embedding/createPresignedUrl/{project_id}",
            json=request.model_dump(exclude_none=True, by_alias=True),
        )
        return self._parse_response(data, EmbeddingResponse)
