"""Basic usage examples for the Hex Python SDK."""

import os

from hex_api import HexClient
from hex_api.models.projects import SortBy, SortDirection

# Initialize the client
# You can pass the API key directly or set HEX_API_KEY environment variable
client = HexClient(api_key=os.getenv("HEX_API_KEY"))

# List all projects
print("Listing all projects:")
projects = client.projects.list(limit=5)
for project in projects.values:
    print(f"  - {project.title} ({project.id})")
    print(f"    Type: {project.type}")
    print(f"    Created: {project.created_at}")
    print(f"    Last edited: {project.last_edited_at}")
    print()

# Get a specific project
if projects.values:
    project_id = projects.values[0].id
    print(f"Getting details for project {project_id}:")
    project = client.projects.get(project_id, include_sharing=True)

    print(f"  Title: {project.title}")
    print(f"  Description: {project.description}")
    print(f"  Owner: {project.owner.email}")
    print(f"  Status: {project.status.name if project.status else 'N/A'}")

    if project.sharing:
        print(f"  Workspace access: {project.sharing.workspace.access}")
        print(f"  Public web access: {project.sharing.public_web.access}")

# List projects with filters
print("\nListing projects with filters:")
filtered_projects = client.projects.list(
    include_archived=False,
    include_components=True,
    sort_by=SortBy.LAST_EDITED_AT,
    sort_direction=SortDirection.DESC,
    limit=10
)

print(f"Found {len(filtered_projects.values)} projects")

# Using pagination
if filtered_projects.pagination.after:
    print("\nFetching next page:")
    next_page = client.projects.list(
        after=filtered_projects.pagination.after,
        limit=10
    )
    print(f"Next page has {len(next_page.values)} projects")
