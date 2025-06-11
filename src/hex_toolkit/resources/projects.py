"""Projects resource for the Hex API SDK."""

import builtins
from typing import Any
from uuid import UUID

from hex_toolkit.models.projects import (
    Project,
    ProjectList,
    SortBy,
    SortDirection,
)
from hex_toolkit.models.runs import ProjectRunResponse, RunProjectRequest
from hex_toolkit.resources.base import BaseResource


class ProjectsResource(BaseResource):
    """Resource for project-related API endpoints."""

    def get(
        self, project_id: str | UUID, include_sharing: bool = False
    ) -> Project:
        """Get metadata about a single project.

        Args:
            project_id: Unique ID for the project
            include_sharing: Whether to include sharing information

        Returns:
            Project details
        """
        params = {"includeSharing": include_sharing}
        data = self._get(f"/v1/projects/{project_id}", params=params)
        return self._parse_response(data, Project)

    def list(
        self,
        include_archived: bool = False,
        include_components: bool = False,
        include_trashed: bool = False,
        include_sharing: bool = False,
        statuses: list[str] | None = None,
        categories: list[str] | None = None,
        creator_email: str | None = None,
        owner_email: str | None = None,
        collection_id: str | None = None,
        limit: int = 25,
        after: str | None = None,
        before: str | None = None,
        sort_by: SortBy | None = None,
        sort_direction: SortDirection | None = None,
    ) -> ProjectList:
        """List all viewable projects.

        Args:
            include_archived: Include archived projects
            include_components: Include component projects
            include_trashed: Include trashed projects
            include_sharing: Include sharing information
            statuses: Filter by project statuses
            categories: Filter by categories
            creator_email: Filter by creator email
            owner_email: Filter by owner email
            collection_id: Filter by collection ID
            limit: Number of results per page (1-100)
            after: Cursor for next page
            before: Cursor for previous page
            sort_by: Sort field
            sort_direction: Sort direction

        Returns:
            ProjectList with projects and pagination info
        """
        params: dict[str, Any] = {
            "includeArchived": include_archived,
            "includeComponents": include_components,
            "includeTrashed": include_trashed,
            "includeSharing": include_sharing,
            "limit": limit,
        }

        if statuses:
            params["statuses"] = statuses
        if categories:
            params["categories"] = categories
        if creator_email:
            params["creatorEmail"] = creator_email
        if owner_email:
            params["ownerEmail"] = owner_email
        if collection_id:
            params["collectionId"] = collection_id
        if after:
            params["after"] = after
        if before:
            params["before"] = before
        if sort_by:
            params["sortBy"] = sort_by.value if isinstance(sort_by, SortBy) else sort_by
        if sort_direction:
            params["sortDirection"] = (
                sort_direction.value
                if isinstance(sort_direction, SortDirection)
                else sort_direction
            )

        data = self._get("/v1/projects", params=params)
        return self._parse_response(data, ProjectList)

    def run(
        self,
        project_id: str | UUID,
        input_params: dict[str, Any] | None = None,
        dry_run: bool = False,
        notifications: builtins.list[dict[str, Any]] | None = None,
        update_published_results: bool = False,
        use_cached_sql_results: bool = True,
        view_id: str | None = None,
    ) -> ProjectRunResponse:
        """Trigger a run of the latest published version of a project.

        Args:
            project_id: Unique ID for the project
            input_params: Input parameters for the run
            dry_run: Whether to perform a dry run
            notifications: Notification configurations
            update_published_results: Update cached state of published app
            use_cached_sql_results: Use cached SQL results
            view_id: Saved view ID to use

        Returns:
            ProjectRunResponse with run information
        """
        request = RunProjectRequest(
            input_params=input_params,
            dry_run=dry_run,
            notifications=notifications,
            update_published_results=update_published_results,
            use_cached_sql_results=use_cached_sql_results,
            view_id=view_id,
        )

        data = self._post(
            f"/v1/projects/{project_id}/runs",
            json=request.model_dump(exclude_none=True, by_alias=True),
        )
        return self._parse_response(data, ProjectRunResponse)
