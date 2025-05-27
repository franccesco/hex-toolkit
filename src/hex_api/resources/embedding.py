"""Embedding resource for the Hex API SDK."""

from hex_api.resources.base import BaseResource


class EmbeddingResource(BaseResource):
    """Resource for embedding-related API endpoints."""

    def create_presigned_url(
        self,
        project_id,
        hex_user_attributes=None,
        scope=None,
        input_parameters=None,
        expires_in=None,
        display_options=None,
        test_mode=False,
    ):
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
            Dict with 'url' key containing the presigned URL
        """
        # Build request data
        request_data = {}
        if hex_user_attributes is not None:
            request_data["hexUserAttributes"] = hex_user_attributes
        if scope is not None:
            request_data["scope"] = scope
        if input_parameters is not None:
            request_data["inputParameters"] = input_parameters
        if expires_in is not None:
            request_data["expiresIn"] = expires_in
        if display_options is not None:
            request_data["displayOptions"] = display_options
        if test_mode:
            request_data["testMode"] = test_mode

        return self._post(
            f"/v1/embedding/createPresignedUrl/{project_id}",
            json=request_data,
        )
