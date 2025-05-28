"""Semantic models resource for the Hex API SDK."""

from hex_toolkit.resources.base import BaseResource


class SemanticModelsResource(BaseResource):
    """Resource for semantic model-related API endpoints."""

    def ingest(
        self,
        semantic_model_id,
        verbose=True,
        debug=False,
        dry_run=False,
    ):
        """Ingest a semantic model from a zip file.

        Note: This endpoint requires sending a zip file as multipart/form-data.
        The current implementation only supports the request parameters.

        Args:
            semantic_model_id: Unique ID for the semantic model
            verbose: Whether to respond with detail on synced components
            debug: Whether to include additional debug information
            dry_run: If enabled, the sync will not write to the database

        Returns:
            Sync response dict with warnings and debug information
        """
        # Build request data
        request_data = {
            "verbose": verbose,
            "debug": debug,
        }
        if dry_run:
            request_data["dryRun"] = dry_run

        # TODO: Add support for file upload when needed
        # This would require passing a file parameter and using multipart/form-data
        return self._post(
            f"/v1/semantic-models/{semantic_model_id}/ingest",
            json=request_data,
        )
