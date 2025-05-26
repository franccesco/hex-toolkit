"""Runs resource for the Hex API SDK."""

from typing import Optional, Union
from uuid import UUID

from hex_api.models.runs import (
    ProjectRunsResponse,
    ProjectStatusResponse,
    RunStatus,
)
from hex_api.resources.base import BaseResource


class RunsResource(BaseResource):
    """Resource for run-related API endpoints."""

    def get_status(
        self,
        project_id: Union[str, UUID],
        run_id: Union[str, UUID],
    ) -> ProjectStatusResponse:
        """Get the status of a project run.

        Args:
            project_id: Unique ID for the project
            run_id: Unique ID for the run

        Returns:
            Run status information
        """
        data = self._get(f"/v1/projects/{project_id}/runs/{run_id}")
        return self._parse_response(data, ProjectStatusResponse)

    def list(
        self,
        project_id: Union[str, UUID],
        limit: int = 25,
        offset: int = 0,
        status_filter: Optional[RunStatus] = None,
    ) -> ProjectRunsResponse:
        """Get the status of API-triggered runs of a project.

        Args:
            project_id: Unique ID for the project
            limit: Number of results per page (1-100)
            offset: Offset for pagination
            status_filter: Filter by run status

        Returns:
            List of run statuses
        """
        params = {
            "limit": limit,
            "offset": offset,
        }
        
        if status_filter:
            params["statusFilter"] = status_filter.value

        data = self._get(f"/v1/projects/{project_id}/runs", params=params)
        return self._parse_response(data, ProjectRunsResponse)

    def cancel(
        self,
        project_id: Union[str, UUID],
        run_id: Union[str, UUID],
    ) -> None:
        """Cancel a project run.

        Args:
            project_id: Unique ID for the project
            run_id: Unique ID for the run
        """
        self._delete(f"/v1/projects/{project_id}/runs/{run_id}")