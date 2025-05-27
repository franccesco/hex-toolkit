"""Command-line interface for Hex API SDK."""

import os
import time
from typing import Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from hex_api import HexClient, __version__
from hex_api.exceptions import HexAPIError

app = typer.Typer(
    help="Hex API CLI - Manage projects and runs via command line",
    invoke_without_command=True,
)
console = Console()

# Create subcommands for better organization
projects_app = typer.Typer(help="Manage Hex projects")
runs_app = typer.Typer(help="Manage project runs")

app.add_typer(projects_app, name="projects")
app.add_typer(runs_app, name="runs")


def get_client():
    """Get an authenticated Hex client instance."""
    api_key = os.getenv("HEX_API_KEY")
    if not api_key:
        console.print("[red]Error: HEX_API_KEY environment variable not set[/red]")
        raise typer.Exit(1)

    api_base_url = os.getenv("HEX_API_BASE_URL")
    return HexClient(api_key=api_key, api_base_url=api_base_url)


@projects_app.command("list")
def list_projects(
    limit: int = typer.Option(25, help="Number of results per page (1-100)"),
    include_archived: bool = typer.Option(False, help="Include archived projects"),
    include_trashed: bool = typer.Option(False, help="Include trashed projects"),
    creator_email: Optional[str] = typer.Option(None, help="Filter by creator email"),
    owner_email: Optional[str] = typer.Option(None, help="Filter by owner email"),
):
    """List all viewable projects."""
    try:
        client = get_client()
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
            )

        projects = response.get("values", [])

        if not projects:
            console.print("[yellow]No projects found[/yellow]")
            return

        # Create a table for display
        table = Table(title="Hex Projects")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Status", style="yellow")
        table.add_column("Owner")
        table.add_column("Created At")

        for project in projects:
            # Handle status which might be a dict or string
            status = project.get("status", "")
            if isinstance(status, dict):
                status = status.get("name", str(status))

            # Try different field names for owner
            owner = ""
            if project.get("owner"):
                owner = project["owner"].get("email", "")
            if not owner:
                owner = project.get("ownerEmail", "")

            # Try different field names for project name
            name = project.get(
                "title", project.get("name", project.get("displayName", ""))
            )

            table.add_row(
                project.get("id", project.get("projectId", "")),
                name,
                status,
                owner,
                project.get("createdAt", "")[:10] if project.get("createdAt") else "",
            )

        console.print(table)

        # Show pagination info if available
        pagination = response.get("pagination", {})
        if pagination.get("hasMore"):
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

        # Display project details
        console.print("\n[bold]Project Details[/bold]")
        console.print(f"ID: [cyan]{project.get('id', project_id)}[/cyan]")

        # Try different field names for project name
        name = project.get("title", project.get("name", "N/A"))
        console.print(f"Name: [green]{name}[/green]")

        # Handle status which might be a dict or string
        status = project.get("status", "N/A")
        if isinstance(status, dict):
            status = status.get("name", str(status))
        console.print(f"Status: [yellow]{status}[/yellow]")

        console.print(f"Description: {project.get('description', 'N/A')}")

        # Try different field names for owner
        owner = "N/A"
        if project.get("owner"):
            owner = project["owner"].get("email", "N/A")
        if owner == "N/A":
            owner = project.get("ownerEmail", "N/A")
        console.print(f"Owner: {owner}")
        console.print(f"Created: {project.get('createdAt', '')[:10]}")
        console.print(f"Last Edited: {project.get('lastEditedAt', '')[:10]}")
        console.print(f"Published Version: {project.get('publishedVersion', 'N/A')}")

        if include_sharing and project.get("sharing"):
            console.print("\n[bold]Sharing Information[/bold]")
            console.print(f"Visibility: {project['sharing'].get('visibility')}")
            console.print(f"Access Level: {project['sharing'].get('accessLevel')}")

    except HexAPIError as e:
        console.print(f"[red]API Error: {e}[/red]")
        raise typer.Exit(1) from e
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1) from e


@projects_app.command("run")
def run_project(
    project_id: str = typer.Argument(help="Unique ID for the project"),
    dry_run: bool = typer.Option(False, help="Perform a dry run"),
    update_cache: bool = typer.Option(
        False, help="Update cached state of published app"
    ),
    no_sql_cache: bool = typer.Option(False, help="Don't use cached SQL results"),
    input_params: Optional[str] = typer.Option(
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
    status: Optional[str] = typer.Option(None, help="Filter by run status"),
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


def _format_status(status: Optional[str]) -> str:
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


@app.callback()
def main(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", "-v", help="Show version"),
):
    """Hex API CLI - Manage projects and runs via command line."""
    if version:
        console.print(f"hex-api version {__version__}")
        raise typer.Exit()

    # If no command was provided, show help
    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help())
        raise typer.Exit()


if __name__ == "__main__":
    app()
