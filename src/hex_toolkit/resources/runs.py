"""Runs resource for the Hex API SDK."""

from typing import Any
from uuid import UUID

from hex_toolkit.models.runs import (
    ProjectRunsResponse,
    ProjectStatusResponse,
    RunStatus,
)
from hex_toolkit.resources.base import BaseResource


class RunsResource(BaseResource):
    """Resource for run-related API endpoints."""

    def get_status(
        self,
        project_id: str | UUID,
        run_id: str | UUID,
    ) -> ProjectStatusResponse:
        """Get the status of a project run.

        Args:
            project_id: Unique ID for the project
            run_id: Unique ID for the run

        Returns:
            ProjectStatusResponse with run status information
        """
        data = self._get(f"/v1/projects/{project_id}/runs/{run_id}")
        return self._parse_response(data, ProjectStatusResponse)

    def list(
        self,
        project_id: str | UUID,
        limit: int | None = None,
        offset: int | None = None,
        status_filter: RunStatus | None = None,
    ) -> ProjectRunsResponse:
        """Get the status of the API-triggered runs for a project.

        Args:
            project_id: Unique ID for the project
            limit: Maximum number of runs to return
            offset: Number of runs to skip
            status_filter: Filter by run status

        Returns:
            ProjectRunsResponse with list of runs and pagination info
        """
        params = {}
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        if status_filter is not None:
            params["statusFilter"] = (
                status_filter.value
                if isinstance(status_filter, RunStatus)
                else status_filter
            )

        data = self._get(f"/v1/projects/{project_id}/runs", params=params)
        return self._parse_response(data, ProjectRunsResponse)

    def cancel(
        self, project_id: str | UUID, run_id: str | UUID
    ) -> dict[str, Any]:
        """Kill a run that was invoked via the API.

        Args:
            project_id: Unique ID for the project
            run_id: Unique ID for the run

        Returns:
            Cancellation result
        """
        return self._delete(f"/v1/projects/{project_id}/runs/{run_id}")
