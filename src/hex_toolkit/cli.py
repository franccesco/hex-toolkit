"""Command-line interface for Hex API SDK."""

import os
import time

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from hex_toolkit import HexClient, __version__
from hex_toolkit.exceptions import HexAPIError

app = typer.Typer(
    help="Hex API CLI - Manage projects and runs via command line",
    invoke_without_command=True,
)
console = Console()

# Create subcommands for better organization
projects_app = typer.Typer(help="Manage Hex projects")
runs_app = typer.Typer(help="Manage project runs")
mcp_app = typer.Typer(help="MCP (Model Context Protocol) server management")

app.add_typer(projects_app, name="projects")
app.add_typer(runs_app, name="runs")
app.add_typer(mcp_app, name="mcp")


def get_client():
    """Get an authenticated Hex client instance."""
    api_key = os.getenv("HEX_API_KEY")
    if not api_key:
        console.print("[red]Error: HEX_API_KEY environment variable not set[/red]")
        raise typer.Exit(1)

    base_url = os.getenv("HEX_API_BASE_URL")
    return HexClient(api_key=api_key, base_url=base_url)


@projects_app.command("list")
def list_projects(
    limit: int = typer.Option(25, help="Number of results per page (1-100)"),
    include_archived: bool = typer.Option(False, help="Include archived projects"),
    include_trashed: bool = typer.Option(False, help="Include trashed projects"),
    creator_email: str | None = typer.Option(None, help="Filter by creator email"),
    owner_email: str | None = typer.Option(None, help="Filter by owner email"),
    sort: str | None = typer.Option(
        None,
        help="Sort by field. Use 'created_at', 'last_edited_at', or 'last_published_at'. "
        "Prefix with '-' for descending order (e.g., '-created_at')",
    ),
    columns: str | None = typer.Option(
        None,
        help="Comma-separated list of columns to display. "
        "Available: id, name, status, owner, created_at, creator, last_viewed_at, app_views. "
        "Default: id, name, status, owner, created_at",
    ),
    search: str | None = typer.Option(
        None,
        help="Search for projects by name or description (case-insensitive). "
        "Fetches all projects and filters locally.",
    ),
):
    """List all viewable projects."""
    try:
        client = get_client()

        # Parse sort option
        sort_by = None
        sort_direction = None
        if sort:
            # Check if it starts with '-' for descending order
            if sort.startswith("-"):
                sort_direction = "DESC"
                sort_field = sort[1:]  # Remove the '-' prefix
            else:
                sort_direction = "ASC"
                sort_field = sort

            # Map CLI field names to API field names
            sort_field_map = {
                "created_at": "CREATED_AT",
                "last_edited_at": "LAST_EDITED_AT",
                "last_published_at": "LAST_PUBLISHED_AT",
            }

            if sort_field in sort_field_map:
                sort_by = sort_field_map[sort_field]
            else:
                console.print(
                    f"[red]Error: Invalid sort field '{sort_field}'. "
                    f"Valid options are: created_at, last_edited_at, last_published_at[/red]"
                )
                raise typer.Exit(1)

        # If searching, we need to fetch all projects
        if search:
            projects = []
            after_cursor = None
            search_lower = search.lower().strip()

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                transient=True,
            ) as progress:
                task = progress.add_task(
                    description="Searching projects...", total=None
                )

                # Fetch all pages
                while True:
                    response = client.projects.list(
                        limit=100,  # Max limit for faster fetching
                        include_archived=include_archived,
                        include_trashed=include_trashed,
                        creator_email=creator_email,
                        owner_email=owner_email,
                        sort_by=sort_by,
                        sort_direction=sort_direction,
                        after=after_cursor,
                    )

                    page_projects = response.get("values", [])

                    # Filter projects that match the search string
                    for project in page_projects:
                        # Get project name
                        name = project.get(
                            "title", project.get("name", project.get("displayName", ""))
                        )
                        if name:
                            name = name.strip()

                        # Get description
                        description = project.get("description") or ""

                        # Check if search string is in name or description (case-insensitive)
                        if (search_lower in name.lower()) or (
                            search_lower in description.lower()
                        ):
                            projects.append(project)

                    # Update progress
                    progress.update(
                        task,
                        description=f"Searching projects... (found {len(projects)} matches)",
                    )

                    # Check if there are more pages
                    pagination = response.get("pagination", {})
                    after_cursor = pagination.get("after")

                    if not after_cursor or not page_projects:
                        break

        else:
            # Normal listing without search
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                transient=True,
            ) as progress:
                progress.add_task(description="Fetching projects...", total=None)
                response = client.projects.list(
                    limit=limit,
                    include_archived=include_archived,
                    include_trashed=include_trashed,
                    creator_email=creator_email,
                    owner_email=owner_email,
                    sort_by=sort_by,
                    sort_direction=sort_direction,
                )

            projects = response.get("values", [])

        if not projects:
            console.print("[yellow]No projects found[/yellow]")
            return

        # Parse columns option
        if columns:
            selected_columns = [col.strip().lower() for col in columns.split(",")]
        else:
            selected_columns = ["id", "name", "status", "owner", "created_at"]

        # Define available columns
        column_definitions = {
            "id": ("ID", "cyan"),
            "name": ("Name", "green"),
            "status": ("Status", "yellow"),
            "owner": ("Owner", None),
            "created_at": ("Created At", None),
            "creator": ("Creator", None),
            "last_viewed_at": ("Last Viewed At", None),
            "app_views": ("App Views (All Time)", None),
        }

        # Create a table for display
        if search:
            table = Table(title=f"Hex Projects (search: '{search}')")
        else:
            table = Table(title="Hex Projects")

        # Add selected columns to table
        for col_key in selected_columns:
            if col_key in column_definitions:
                col_name, col_style = column_definitions[col_key]
                table.add_column(col_name, style=col_style)

        for project in projects:
            # Build row data based on selected columns
            row_data = []

            for col_key in selected_columns:
                if col_key == "id":
                    row_data.append(project.get("id", project.get("projectId", "")))

                elif col_key == "name":
                    # Try different field names for project name
                    name = project.get(
                        "title", project.get("name", project.get("displayName", ""))
                    )
                    if name:
                        name = name.strip()
                    row_data.append(name)

                elif col_key == "status":
                    # Handle status which might be a dict or string
                    status = project.get("status", "")
                    if isinstance(status, dict):
                        status = status.get("name", str(status))
                    row_data.append(status)

                elif col_key == "owner":
                    # Try different field names for owner
                    owner = ""
                    if project.get("owner"):
                        owner = project["owner"].get("email", "")
                    if not owner:
                        owner = project.get("ownerEmail", "")
                    row_data.append(owner)

                elif col_key == "created_at":
                    row_data.append(
                        project.get("createdAt", "")[:10]
                        if project.get("createdAt")
                        else ""
                    )

                elif col_key == "creator":
                    # Get creator email
                    creator = ""
                    if project.get("creator"):
                        creator = project["creator"].get("email", "")
                    row_data.append(creator)

                elif col_key == "last_viewed_at":
                    # Get last viewed timestamp from analytics
                    last_viewed = ""
                    if project.get("analytics") and project["analytics"].get(
                        "lastViewedAt"
                    ):
                        last_viewed = project["analytics"]["lastViewedAt"][:10]
                    row_data.append(last_viewed)

                elif col_key == "app_views":
                    # Get app views all time from analytics
                    app_views = ""
                    if project.get("analytics") and project["analytics"].get(
                        "appViews"
                    ):
                        app_views = str(
                            project["analytics"]["appViews"].get("allTime", "")
                        )
                    row_data.append(app_views)

            table.add_row(*row_data)

        console.print(table)

        # Show pagination info if available
        if search:
            console.print(
                f"\n[dim]Found {len(projects)} project(s) matching '{search}'[/dim]"
            )
        else:
            pagination = response.get("pagination", {})
            if pagination.get("after"):
                console.print(
                    "\n[dim]More results available. Use --limit to see more.[/dim]"
                )

    except HexAPIError as e:
        console.print(f"[red]API Error: {e}[/red]")
        raise typer.Exit(1) from e
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1) from e


@projects_app.command("get")
def get_project(
    project_id: str = typer.Argument(help="Unique ID for the project"),
    include_sharing: bool = typer.Option(False, help="Include sharing information"),
):
    """Get metadata about a single project."""
    try:
        client = get_client()
        project = client.projects.get(project_id, include_sharing=include_sharing)

        # Extract basic information
        name = project.get("title", project.get("name", "Untitled"))
        if name:
            name = name.strip()

        project_type = project.get("type", "PROJECT")

        # Create main panel with project name
        console.print()
        console.print(Panel(f"[bold cyan]{name}[/bold cyan]", expand=False))

        # Basic Information Section
        console.print("\n[bold]📋 Basic Information[/bold]")
        info_table = Table(show_header=False, box=None, padding=(0, 2))
        info_table.add_column(style="dim")
        info_table.add_column()

        info_table.add_row("ID", f"[cyan]{project.get('id', project_id)}[/cyan]")
        info_table.add_row("Type", project_type)

        # Description
        description = project.get("description")
        if description:
            # Clean up description
            description = " ".join(description.split())
            if len(description) > 100:
                description = description[:97] + "..."
            info_table.add_row("Description", description)

        # Status
        status = project.get("status")
        if isinstance(status, dict):
            status_name = status.get("name", "Unknown")
        else:
            status_name = str(status) if status else "Unknown"

        status_color = "green" if status_name == "Published" else "yellow"
        info_table.add_row("Status", f"[{status_color}]{status_name}[/{status_color}]")

        # Published version
        published_version = project.get("publishedVersion")
        if published_version:
            info_table.add_row("Published Version", str(published_version))

        console.print(info_table)

        # People Section
        console.print("\n[bold]👥 People[/bold]")
        people_table = Table(show_header=False, box=None, padding=(0, 2))
        people_table.add_column(style="dim")
        people_table.add_column()

        # Creator
        if project.get("creator"):
            creator_email = project["creator"].get("email", "Unknown")
            people_table.add_row("Creator", creator_email)

        # Owner
        owner_email = "Unknown"
        if project.get("owner"):
            owner_email = project["owner"].get("email", "Unknown")
        elif project.get("ownerEmail"):
            owner_email = project.get("ownerEmail")
        people_table.add_row("Owner", owner_email)

        console.print(people_table)

        # Timestamps Section
        console.print("\n[bold]🕐 Timestamps[/bold]")
        time_table = Table(show_header=False, box=None, padding=(0, 2))
        time_table.add_column(style="dim")
        time_table.add_column()

        # Format timestamps
        created_at = project.get("createdAt", "")
        if created_at:
            time_table.add_row("Created", _format_timestamp(created_at))

        last_edited = project.get("lastEditedAt", "")
        if last_edited:
            time_table.add_row("Last Edited", _format_timestamp(last_edited))

        last_published = project.get("lastPublishedAt")
        if last_published:
            time_table.add_row("Last Published", _format_timestamp(last_published))

        archived_at = project.get("archivedAt")
        if archived_at:
            time_table.add_row(
                "Archived", f"[red]{_format_timestamp(archived_at)}[/red]"
            )

        trashed_at = project.get("trashedAt")
        if trashed_at:
            time_table.add_row("Trashed", f"[red]{_format_timestamp(trashed_at)}[/red]")

        console.print(time_table)

        # Analytics Section
        analytics = project.get("analytics")
        if analytics:
            console.print("\n[bold]📊 Analytics[/bold]")
            analytics_table = Table(show_header=False, box=None, padding=(0, 2))
            analytics_table.add_column(style="dim")
            analytics_table.add_column()

            # Last viewed
            last_viewed = analytics.get("lastViewedAt")
            if last_viewed:
                analytics_table.add_row("Last Viewed", _format_timestamp(last_viewed))

            # Published results updated
            pub_results = analytics.get("publishedResultsUpdatedAt")
            if pub_results:
                analytics_table.add_row(
                    "Results Updated", _format_timestamp(pub_results)
                )

            # App views
            app_views = analytics.get("appViews")
            if app_views:
                views_str = []
                if app_views.get("allTime"):
                    views_str.append(f"All time: {app_views['allTime']:,}")
                if app_views.get("lastThirtyDays"):
                    views_str.append(f"30d: {app_views['lastThirtyDays']:,}")
                if app_views.get("lastSevenDays"):
                    views_str.append(f"7d: {app_views['lastSevenDays']:,}")

                if views_str:
                    analytics_table.add_row("App Views", " | ".join(views_str))

            if analytics_table.row_count > 0:
                console.print(analytics_table)

        # Categories Section
        categories = project.get("categories", [])
        if categories:
            console.print("\n[bold]🏷️  Categories[/bold]")
            for cat in categories:
                cat_name = cat.get("name", "Unknown")
                cat_desc = cat.get("description", "")
                if cat_desc:
                    console.print(f"  • {cat_name}: [dim]{cat_desc}[/dim]")
                else:
                    console.print(f"  • {cat_name}")

        # Reviews Section
        reviews = project.get("reviews")
        if reviews:
            console.print("\n[bold]✅ Reviews[/bold]")
            required = reviews.get("required", False)
            console.print(f"  Reviews Required: {'Yes' if required else 'No'}")

        # Schedules Section
        schedules = project.get("schedules", [])
        if schedules:
            console.print("\n[bold]📅 Schedules[/bold]")
            for i, schedule in enumerate(schedules, 1):
                if not schedule.get("enabled"):
                    continue

                cadence = schedule.get("cadence", "Unknown")
                console.print(f"\n  Schedule {i}: [yellow]{cadence}[/yellow]")

                # Show schedule details based on cadence
                if cadence == "HOURLY" and schedule.get("hourly"):
                    details = schedule["hourly"]
                    console.print(
                        f"    Runs at: {details.get('minute', 0)} minutes past each hour"
                    )
                    console.print(f"    Timezone: {details.get('timezone', 'UTC')}")
                elif cadence == "DAILY" and schedule.get("daily"):
                    details = schedule["daily"]
                    console.print(
                        f"    Runs at: {details.get('hour', 0):02d}:{details.get('minute', 0):02d}"
                    )
                    console.print(f"    Timezone: {details.get('timezone', 'UTC')}")
                elif cadence == "WEEKLY" and schedule.get("weekly"):
                    details = schedule["weekly"]
                    console.print(f"    Day: {details.get('dayOfWeek', 'Unknown')}")
                    console.print(
                        f"    Time: {details.get('hour', 0):02d}:{details.get('minute', 0):02d}"
                    )
                    console.print(f"    Timezone: {details.get('timezone', 'UTC')}")
                elif cadence == "MONTHLY" and schedule.get("monthly"):
                    details = schedule["monthly"]
                    console.print(f"    Day: {details.get('day', 1)}")
                    console.print(
                        f"    Time: {details.get('hour', 0):02d}:{details.get('minute', 0):02d}"
                    )
                    console.print(f"    Timezone: {details.get('timezone', 'UTC')}")
                elif cadence == "CUSTOM" and schedule.get("custom"):
                    details = schedule["custom"]
                    console.print(f"    Cron: {details.get('cron', 'Unknown')}")
                    console.print(f"    Timezone: {details.get('timezone', 'UTC')}")

        # Sharing Section (if requested)
        if include_sharing and project.get("sharing"):
            console.print("\n[bold]🔒 Sharing & Permissions[/bold]")
            sharing = project["sharing"]

            # Workspace access
            if sharing.get("workspace"):
                access = sharing["workspace"].get("access", "NONE")
                console.print("\n  [bold]Workspace[/bold]")
                console.print(f"    Access Level: {_format_access_level(access)}")

            # Public web access
            if sharing.get("publicWeb"):
                access = sharing["publicWeb"].get("access", "NONE")
                console.print("\n  [bold]Public Web[/bold]")
                console.print(f"    Access Level: {_format_access_level(access)}")

            # Support access
            if sharing.get("support"):
                access = sharing["support"].get("access", "NONE")
                console.print("\n  [bold]Support[/bold]")
                console.print(f"    Access Level: {_format_access_level(access)}")

            # Users
            users = sharing.get("users", [])
            if users:
                console.print(f"\n  [bold]Users ({len(users)})[/bold]")
                for user in users[:5]:  # Show first 5
                    email = user.get("user", {}).get("email", "Unknown")
                    access = user.get("access", "NONE")
                    console.print(f"    • {email}: {_format_access_level(access)}")
                if len(users) > 5:
                    console.print(f"    ... and {len(users) - 5} more")

            # Groups
            groups = sharing.get("groups", [])
            if groups:
                console.print(f"\n  [bold]Groups ({len(groups)})[/bold]")
                for group in groups:
                    name = group.get("group", {}).get("name", "Unknown")
                    access = group.get("access", "NONE")
                    console.print(f"    • {name}: {_format_access_level(access)}")

            # Collections
            collections = sharing.get("collections", [])
            if collections:
                console.print(f"\n  [bold]Collections ({len(collections)})[/bold]")
                for collection in collections:
                    name = collection.get("collection", {}).get("name", "Unknown")
                    access = collection.get("access", "NONE")
                    console.print(f"    • {name}: {_format_access_level(access)}")

        console.print()  # Empty line at the end

    except HexAPIError as e:
        console.print(f"[red]API Error: {e}[/red]")
        raise typer.Exit(1) from e
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1) from e


def _format_timestamp(timestamp: str) -> str:
    """Format ISO timestamp to a more readable format."""
    if not timestamp:
        return "N/A"

    try:
        # Parse and format the timestamp
        from datetime import datetime

        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))

        # Get current time for relative formatting
        now = datetime.now(dt.tzinfo)
        diff = now - dt

        # Format with relative time if recent
        if diff.days == 0:
            if diff.seconds < 3600:
                mins = diff.seconds // 60
                return f"{dt.strftime('%Y-%m-%d %H:%M')} ({mins}m ago)"
            else:
                hours = diff.seconds // 3600
                return f"{dt.strftime('%Y-%m-%d %H:%M')} ({hours}h ago)"
        elif diff.days == 1:
            return f"{dt.strftime('%Y-%m-%d %H:%M')} (yesterday)"
        elif diff.days < 7:
            return f"{dt.strftime('%Y-%m-%d %H:%M')} ({diff.days}d ago)"
        else:
            return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        # If parsing fails, just return the first part
        return timestamp[:19]


def _format_access_level(access: str) -> str:
    """Format access level with color."""
    access_colors = {
        "NONE": "[red]None[/red]",
        "APP_ONLY": "[yellow]App Only[/yellow]",
        "CAN_VIEW": "[cyan]Can View[/cyan]",
        "CAN_EDIT": "[green]Can Edit[/green]",
        "FULL_ACCESS": "[bold green]Full Access[/bold green]",
    }
    return access_colors.get(access, access)


@projects_app.command("run")
def run_project(
    project_id: str = typer.Argument(help="Unique ID for the project"),
    dry_run: bool = typer.Option(False, help="Perform a dry run"),
    update_cache: bool = typer.Option(
        False, help="Update cached state of published app"
    ),
    no_sql_cache: bool = typer.Option(False, help="Don't use cached SQL results"),
    input_params: str | None = typer.Option(
        None, help="JSON string of input parameters"
    ),
    wait: bool = typer.Option(False, help="Wait for run to complete"),
    poll_interval: int = typer.Option(
        5, help="Polling interval in seconds (when --wait)"
    ),
):
    """Trigger a run of the latest published version of a project."""
    try:
        client = get_client()

        # Parse input parameters if provided
        params = None
        if input_params:
            import json

            try:
                params = json.loads(input_params)
            except json.JSONDecodeError as e:
                console.print("[red]Error: Invalid JSON for input parameters[/red]")
                raise typer.Exit(1) from e

        # Start the run
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task(description="Starting project run...", total=None)
            run_info = client.projects.run(
                project_id,
                input_params=params,
                dry_run=dry_run,
                update_published_results=update_cache,
                use_cached_sql_results=not no_sql_cache,
            )

        run_id = run_info.get("runId", run_info.get("id"))
        console.print("\n[green]✓[/green] Run started successfully!")
        console.print(f"Run ID: [cyan]{run_id}[/cyan]")

        # Handle different possible field names for URLs
        run_url = run_info.get("runUrl", run_info.get("url", "N/A"))
        status_url = run_info.get("runStatusUrl", run_info.get("statusUrl", "N/A"))

        if run_url and run_url != "N/A":
            console.print(f"Run URL: [blue]{run_url}[/blue]")
        if status_url and status_url != "N/A":
            console.print(f"Status URL: [blue]{status_url}[/blue]")

        if wait:
            console.print(
                f"\n[dim]Waiting for run to complete (polling every {poll_interval}s)...[/dim]"
            )
            _wait_for_run_completion(client, project_id, run_id, poll_interval)

    except HexAPIError as e:
        console.print(f"[red]API Error: {e}[/red]")
        raise typer.Exit(1) from e
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1) from e


@runs_app.command("status")
def get_run_status(
    project_id: str = typer.Argument(help="Unique ID for the project"),
    run_id: str = typer.Argument(help="Unique ID for the run"),
):
    """Get the status of a project run."""
    try:
        client = get_client()
        status = client.runs.get_status(project_id, run_id)

        console.print("\n[bold]Run Status[/bold]")
        console.print(
            f"Run ID: [cyan]{status.get('runId', status.get('id', 'N/A'))}[/cyan]"
        )
        console.print(f"Project ID: [cyan]{status.get('projectId', project_id)}[/cyan]")
        console.print(f"Status: {_format_status(status.get('status'))}")
        console.print(
            f"Started: {status.get('startTime', status.get('startedAt', 'N/A'))}"
        )
        console.print(f"Ended: {status.get('endTime', status.get('endedAt', 'N/A'))}")

        if status.get("error"):
            console.print(f"\n[red]Error: {status.get('error')}[/red]")

    except HexAPIError as e:
        console.print(f"[red]API Error: {e}[/red]")
        raise typer.Exit(1) from e
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1) from e


@runs_app.command("list")
def list_runs(
    project_id: str = typer.Argument(help="Unique ID for the project"),
    limit: int = typer.Option(10, help="Maximum number of runs to return"),
    offset: int = typer.Option(0, help="Number of runs to skip"),
    status: str | None = typer.Option(None, help="Filter by run status"),
):
    """Get the status of API-triggered runs for a project."""
    try:
        client = get_client()
        response = client.runs.list(
            project_id,
            limit=limit,
            offset=offset,
            status_filter=status,
        )

        runs = response.get("runs", [])

        if not runs:
            console.print("[yellow]No runs found[/yellow]")
            return

        # Create a table for display
        table = Table(title=f"Runs for Project {project_id}")
        table.add_column("Run ID", style="cyan")
        table.add_column("Status", style="yellow")
        table.add_column("Started")
        table.add_column("Ended")
        table.add_column("Duration")

        for run in runs:
            # Try different field names
            run_id = run.get("runId", run.get("id", ""))
            start_time = run.get("startTime", run.get("startedAt", ""))
            end_time = run.get("endTime", run.get("endedAt", ""))
            duration = (
                _calculate_duration(start_time, end_time)
                if start_time and end_time
                else "N/A"
            )

            table.add_row(
                run_id,
                _format_status(run.get("status")),
                start_time[:19] if start_time else "N/A",
                end_time[:19] if end_time else "N/A",
                duration,
            )

        console.print(table)

        # Show total count
        total = response.get("totalCount", 0)
        if total > len(runs):
            console.print(f"\n[dim]Showing {len(runs)} of {total} total runs[/dim]")

    except HexAPIError as e:
        console.print(f"[red]API Error: {e}[/red]")
        raise typer.Exit(1) from e
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1) from e


@runs_app.command("cancel")
def cancel_run(
    project_id: str = typer.Argument(help="Unique ID for the project"),
    run_id: str = typer.Argument(help="Unique ID for the run"),
    confirm: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
):
    """Cancel a run that was invoked via the API."""
    try:
        if not confirm:
            confirm = typer.confirm(f"Are you sure you want to cancel run {run_id}?")
            if not confirm:
                console.print("[yellow]Cancelled[/yellow]")
                return

        client = get_client()
        client.runs.cancel(project_id, run_id)

        console.print(f"[green]✓[/green] Run {run_id} cancelled successfully")

    except HexAPIError as e:
        console.print(f"[red]API Error: {e}[/red]")
        raise typer.Exit(1) from e
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1) from e


def _format_status(status: str | None) -> str:
    """Format run status with color."""
    if not status:
        return "N/A"

    status_colors = {
        "PENDING": "[yellow]PENDING[/yellow]",
        "RUNNING": "[blue]RUNNING[/blue]",
        "COMPLETED": "[green]COMPLETED[/green]",
        "FAILED": "[red]FAILED[/red]",
        "CANCELLED": "[red]CANCELLED[/red]",
        "KILLED": "[red]KILLED[/red]",
    }

    return status_colors.get(status.upper(), status)


def _calculate_duration(start_time: str, end_time: str) -> str:
    """Calculate duration between two timestamps."""
    try:
        from datetime import datetime

        start = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
        end = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
        duration = end - start

        # Format duration
        seconds = int(duration.total_seconds())
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            return f"{seconds // 60}m {seconds % 60}s"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}h {minutes}m"
    except Exception:
        return "N/A"


def _wait_for_run_completion(client, project_id: str, run_id: str, poll_interval: int):
    """Wait for a run to complete, polling periodically."""
    terminal_states = {"COMPLETED", "FAILED", "CANCELLED", "KILLED"}

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
    ) as progress:
        task = progress.add_task(
            description="Waiting for run completion...", total=None
        )

        while True:
            try:
                status = client.runs.get_status(project_id, run_id)
                current_status = status.get("status", "").upper()

                progress.update(task, description=f"Status: {current_status}")

                if current_status in terminal_states:
                    progress.stop()
                    console.print(
                        f"\nRun completed with status: {_format_status(current_status)}"
                    )

                    if current_status == "FAILED" and status.get("error"):
                        console.print(f"[red]Error: {status.get('error')}[/red]")

                    break

                time.sleep(poll_interval)

            except KeyboardInterrupt:
                progress.stop()
                console.print("\n[yellow]Polling cancelled by user[/yellow]")
                break
            except Exception as e:
                progress.stop()
                console.print(f"\n[red]Error during polling: {e}[/red]")
                break


# MCP Commands
@mcp_app.command("serve")
def mcp_serve(
    transport: str = typer.Option("stdio", help="Transport type: stdio, sse"),
    port: int = typer.Option(8080, help="Port for SSE transport"),
    host: str = typer.Option("127.0.0.1", help="Host for SSE transport"),
):
    """Run the Hex Toolkit MCP server."""
    try:
        # Check for API key
        api_key = os.getenv("HEX_API_KEY")
        if not api_key:
            # For stdio transport, don't print to stdout as it breaks MCP protocol
            if transport != "stdio":
                console.print(
                    "[red]Error: HEX_API_KEY environment variable not set[/red]"
                )
            raise typer.Exit(1)

        # Import here to avoid circular imports and only when needed
        from hex_toolkit.mcp import mcp_server

        if transport == "stdio":
            # For stdio transport, don't print to stdout as it breaks MCP JSON protocol
            # Claude Desktop uses stdio and expects clean JSON communication
            mcp_server.run()
        elif transport == "sse":
            console.print(
                f"[green]Starting Hex Toolkit MCP server (SSE transport) on {host}:{port}...[/green]"
            )
            mcp_server.run(transport="sse", sse_host=host, sse_port=port)
        else:
            console.print(f"[red]Unknown transport: {transport}[/red]")
            raise typer.Exit(1)

    except KeyboardInterrupt:
        # For stdio transport, don't print to stdout as it breaks MCP protocol
        if transport != "stdio":
            console.print("\n[yellow]MCP server stopped[/yellow]")
    except Exception as e:
        # For stdio transport, don't print to stdout as it breaks MCP protocol
        if transport != "stdio":
            console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1) from e


@mcp_app.command("install")
def mcp_install(
    target: str = typer.Option(
        "auto", help="Installation target: auto, claude-desktop, claude-code, all"
    ),
    scope: str = typer.Option(
        "user", help="Scope for Claude Code: local, project, user"
    ),
    force: bool = typer.Option(
        False, help="Force installation even if already configured"
    ),
):
    """Install the Hex Toolkit MCP server for Claude Desktop and/or Claude Code."""
    try:
        # Import here to avoid circular imports
        from hex_toolkit.mcp.installer import MCPInstaller

        installer = MCPInstaller()
        installer.install(target=target, scope=scope, force=force)

    except Exception as e:
        console.print(f"[red]Installation failed: {e}[/red]")
        raise typer.Exit(1) from e


@mcp_app.command("uninstall")
def mcp_uninstall(
    target: str = typer.Option(
        "auto", help="Uninstall target: auto, claude-desktop, claude-code, all"
    ),
    scope: str = typer.Option(
        "user", help="Scope for Claude Code: local, project, user"
    ),
):
    """Remove the Hex Toolkit MCP server configuration."""
    try:
        # Import here to avoid circular imports
        from hex_toolkit.mcp.installer import MCPInstaller

        installer = MCPInstaller()
        installer.uninstall(target=target, scope=scope)

    except Exception as e:
        console.print(f"[red]Uninstallation failed: {e}[/red]")
        raise typer.Exit(1) from e


@mcp_app.command("status")
def mcp_status():
    """Check the status of Hex Toolkit MCP server installation."""
    try:
        # Import here to avoid circular imports
        from hex_toolkit.mcp.installer import MCPInstaller

        installer = MCPInstaller()
        installer.status()

    except Exception as e:
        console.print(f"[red]Status check failed: {e}[/red]")
        raise typer.Exit(1) from e


@app.callback()
def main(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", "-v", help="Show version"),
):
    """Hex Toolkit CLI - Manage projects and runs via command line."""
    if version:
        console.print(f"hex-toolkit version {__version__}")
        raise typer.Exit()

    # If no command was provided, show help
    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help())
        raise typer.Exit()


if __name__ == "__main__":
    app()
