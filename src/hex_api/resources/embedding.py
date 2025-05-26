"""Embedding resource for the Hex API SDK."""

from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from hex_api.models.embedding import (
    DisplayOptions,
    EmbeddingRequest,
    EmbeddingResponse,
    ThemeType,
)
from hex_api.resources.base import BaseResource


class EmbeddingResource(BaseResource):
    """Resource for embedding-related API endpoints."""

    def create_presigned_url(
        self,
        project_id: Union[str, UUID],
        hex_user_attributes: Optional[Dict[str, str]] = None,
        scope: Optional[List[str]] = None,
        input_parameters: Optional[Dict[str, Any]] = None,
        expires_in: Optional[float] = None,
        display_options: Optional[DisplayOptions] = None,
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
            Presigned URL for embedding
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