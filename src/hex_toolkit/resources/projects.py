"""Projects resource for the Hex API SDK."""

from hex_toolkit.resources.base import BaseResource


class ProjectsResource(BaseResource):
    """Resource for project-related API endpoints."""

    def get(self, project_id, include_sharing=False):
        """Get metadata about a single project.

        Args:
            project_id: Unique ID for the project
            include_sharing: Whether to include sharing information

        Returns:
            Project details as a dict
        """
        params = {"includeSharing": include_sharing}
        return self._get(f"/v1/projects/{project_id}", params=params)

    def list(
        self,
        include_archived=False,
        include_components=False,
        include_trashed=False,
        include_sharing=False,
        statuses=None,
        categories=None,
        creator_email=None,
        owner_email=None,
        collection_id=None,
        limit=25,
        after=None,
        before=None,
        sort_by=None,
        sort_direction=None,
    ):
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
            sort_by: Sort field (e.g., "CREATED_AT", "LAST_EDITED_AT")
            sort_direction: Sort direction ("ASC" or "DESC")

        Returns:
            Dict with 'values' (list of projects) and 'pagination' info
        """
        params = {
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
            params["sortBy"] = sort_by
        if sort_direction:
            params["sortDirection"] = sort_direction

        return self._get("/v1/projects", params=params)

    def run(
        self,
        project_id,
        input_params=None,
        dry_run=False,
        notifications=None,
        update_published_results=False,
        use_cached_sql_results=True,
        view_id=None,
    ):
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
            Run information dict with run ID and URLs
        """
        # Build request data
        request_data = {}
        if input_params is not None:
            request_data["inputParams"] = input_params
        if dry_run:
            request_data["dryRun"] = dry_run
        if notifications is not None:
            request_data["notifications"] = notifications
        if update_published_results:
            request_data["updatePublishedResults"] = update_published_results
        if not use_cached_sql_results:
            request_data["useCachedSqlResults"] = use_cached_sql_results
        if view_id is not None:
            request_data["viewId"] = view_id

        return self._post(f"/v1/projects/{project_id}/runs", json=request_data)
