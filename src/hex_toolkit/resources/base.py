"""Base resource class for the Hex API SDK."""

from typing import TYPE_CHECKING, Any, TypeVar

from pydantic import BaseModel

if TYPE_CHECKING:
    from hex_toolkit.client import HexClient

T = TypeVar("T", bound=BaseModel)


class BaseResource:
    """Base class for API resources."""

    def __init__(self, client: "HexClient") -> None:
        self._client = client

    def _request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> Any:
        """Make a request through the client."""
        response = self._client.request(method, path, **kwargs)
        return response.json() if response.content else None

    def _get(self, path: str, **kwargs: Any) -> Any:
        """Make a GET request."""
        return self._request("GET", path, **kwargs)

    def _post(self, path: str, **kwargs: Any) -> Any:
        """Make a POST request."""
        return self._request("POST", path, **kwargs)

    def _put(self, path: str, **kwargs: Any) -> Any:
        """Make a PUT request."""
        return self._request("PUT", path, **kwargs)

    def _delete(self, path: str, **kwargs: Any) -> Any:
        """Make a DELETE request."""
        return self._request("DELETE", path, **kwargs)

    def _parse_response(self, response_data: Any, model: type[T]) -> T:
        """Parse response data into a Pydantic model."""
        return model.model_validate(response_data)
