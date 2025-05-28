"""Base resource class for the Hex API SDK."""


class BaseResource:
    """Base class for API resources."""

    def __init__(self, client):
        self._client = client

    def _request(
        self,
        method,
        path,
        **kwargs,
    ):
        """Make a request through the client."""
        response = self._client.request(method, path, **kwargs)
        return response.json() if response.content else None

    def _get(self, path, **kwargs):
        """Make a GET request."""
        return self._request("GET", path, **kwargs)

    def _post(self, path, **kwargs):
        """Make a POST request."""
        return self._request("POST", path, **kwargs)

    def _put(self, path, **kwargs):
        """Make a PUT request."""
        return self._request("PUT", path, **kwargs)

    def _delete(self, path, **kwargs):
        """Make a DELETE request."""
        return self._request("DELETE", path, **kwargs)

    def _parse_response(self, response_data):
        """Return response data as-is (dict or list of dicts)."""
        return response_data
