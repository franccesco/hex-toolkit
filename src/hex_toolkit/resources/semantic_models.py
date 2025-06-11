"""Semantic models resource for the Hex API SDK."""

from uuid import UUID

from hex_toolkit.models.semantic_models import (
    SemanticModelIngestRequest,
    SemanticModelsSyncResponse,
)
from hex_toolkit.resources.base import BaseResource


class SemanticModelsResource(BaseResource):
    """Resource for semantic model-related API endpoints."""

    def ingest(
        self,
        semantic_model_id: str | UUID,
        verbose: bool = True,
        debug: bool = False,
        dry_run: bool = False,
    ) -> SemanticModelsSyncResponse:
        """Ingest a semantic model from a zip file.

        Note: This endpoint requires sending a zip file as multipart/form-data.
        The current implementation only supports the request parameters.

        Args:
            semantic_model_id: Unique ID for the semantic model
            verbose: Whether to respond with detail on synced components
            debug: Whether to include additional debug information
            dry_run: If enabled, the sync will not write to the database

        Returns:
            SemanticModelsSyncResponse with warnings and debug information
        """
        request = SemanticModelIngestRequest(
            verbose=verbose,
            debug=debug,
            dry_run=dry_run,
        )

        # TODO: Add support for file upload when needed
        # This would require passing a file parameter and using multipart/form-data
        data = self._post(
            f"/v1/semantic-models/{semantic_model_id}/ingest",
            json=request.model_dump(exclude_none=True, by_alias=True),
        )
        return self._parse_response(data, SemanticModelsSyncResponse)
