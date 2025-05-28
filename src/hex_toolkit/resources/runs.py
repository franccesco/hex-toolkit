"""Runs resource for the Hex API SDK."""

from hex_toolkit.resources.base import BaseResource


class RunsResource(BaseResource):
    """Resource for run-related API endpoints."""

    def get_status(
        self,
        project_id,
        run_id,
    ):
        """Get the status of a project run.

        Args:
            project_id: Unique ID for the project
            run_id: Unique ID for the run

        Returns:
            Run status information as a dict
        """
        return self._get(f"/v1/projects/{project_id}/runs/{run_id}")

    def list(
        self,
        project_id,
        limit=None,
        offset=None,
        status_filter=None,
    ):
        """Get the status of the API-triggered runs for a project.

        Args:
            project_id: Unique ID for the project
            limit: Maximum number of runs to return
            offset: Number of runs to skip
            status_filter: Filter by run status

        Returns:
            Dict with list of runs and pagination info
        """
        params = {}
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        if status_filter is not None:
            params["statusFilter"] = status_filter

        return self._get(f"/v1/projects/{project_id}/runs", params=params)

    def cancel(self, project_id, run_id):
        """Kill a run that was invoked via the API.

        Args:
            project_id: Unique ID for the project
            run_id: Unique ID for the run

        Returns:
            Cancellation result
        """
        return self._delete(f"/v1/projects/{project_id}/runs/{run_id}")
