"""Example of running a Hex project and monitoring its status."""

import os
import time

from hex_api import HexClient
from hex_api.models.runs import RunStatus


# Example: Run a project and wait for completion
def run_project():
    """Run a project synchronously and wait for completion."""
    client = HexClient(api_key=os.getenv("HEX_API_KEY"))

    # Replace with your project ID
    project_id = "12345678-1234-1234-1234-123456789012"

    # Run the project with input parameters
    print("Starting project run...")
    run = client.projects.run(
        project_id=project_id,
        input_params={
            "date_range": "last_30_days",
            "customer_segment": "premium",
        },
        update_published_results=True,
    )

    print(f"Run started with ID: {run.run_id}")
    print(f"Project version: {run.project_version}")
    print(f"Run URL: {run.run_url}")

    # Poll for status
    print("\nMonitoring run status...")
    while True:
        status = client.runs.get_status(project_id, run.run_id)
        print(f"Status: {status.status}")

        if status.status in [RunStatus.COMPLETED, RunStatus.ERRORED, RunStatus.KILLED]:
            break

        if status.status == RunStatus.RUNNING and status.elapsed_time:
            print(f"  Elapsed time: {status.elapsed_time/1000:.1f}s")

        time.sleep(5)  # Wait 5 seconds before checking again

    # Final status
    print(f"\nRun finished with status: {status.status}")
    if status.elapsed_time:
        print(f"Total time: {status.elapsed_time/1000:.1f}s")

    if status.status == RunStatus.ERRORED:
        print("Run failed!")
        # You might want to check logs or contact support with the trace ID
        print(f"Trace ID for support: {status.trace_id}")


# Example: Dry run to test parameters
def test_run_with_dry_run():
    """Test a project run without actually executing it."""
    client = HexClient(api_key=os.getenv("HEX_API_KEY"))

    project_id = "12345678-1234-1234-1234-123456789012"

    print("Testing project run (dry run)...")
    try:
        run = client.projects.run(
            project_id=project_id,
            input_params={
                "test_param": "test_value",
                "numeric_param": 42,
            },
            dry_run=True,
        )
        print("Dry run successful!")
        print(f"Would have run version: {run.project_version}")
    except Exception as e:
        print(f"Dry run failed: {e}")


# Example: Run with notifications
def run_with_notifications():
    """Run a project with Slack notifications."""
    client = HexClient(api_key=os.getenv("HEX_API_KEY"))

    project_id = "12345678-1234-1234-1234-123456789012"

    print("Starting project run with notifications...")
    run = client.projects.run(
        project_id=project_id,
        input_params={"report_type": "monthly"},
        notifications=[
            {
                "type": "ALL",
                "includeSuccessScreenshot": True,
                "slackChannelIds": ["C0123456789"],
                "subject": "Monthly Report Complete",
                "body": "The monthly report has finished running.",
            }
        ],
    )

    print(f"Run started: {run.run_id}")
    print("Notifications will be sent when the run completes.")


# Example: Cancel a run
def cancel_run_example():
    """Example of canceling a running project."""
    client = HexClient(api_key=os.getenv("HEX_API_KEY"))

    project_id = "12345678-1234-1234-1234-123456789012"

    # Start a run
    run = client.projects.run(project_id=project_id)
    print(f"Started run: {run.run_id}")

    # Wait a bit then cancel
    time.sleep(2)

    print("Canceling run...")
    client.runs.cancel(project_id, run.run_id)
    print("Run canceled")

    # Check final status
    status = client.runs.get_status(project_id, run.run_id)
    print(f"Final status: {status.status}")


# Example: List recent runs
def list_recent_runs():
    """List recent runs for a project."""
    client = HexClient(api_key=os.getenv("HEX_API_KEY"))

    project_id = "12345678-1234-1234-1234-123456789012"

    print("Recent runs:")
    runs = client.runs.list(project_id, limit=5)

    for run in runs.runs:
        print(f"\nRun ID: {run.run_id}")
        print(f"  Status: {run.status}")
        print(f"  Started: {run.start_time}")
        print(f"  Elapsed: {run.elapsed_time/1000:.1f}s" if run.elapsed_time else "  Elapsed: N/A")


if __name__ == "__main__":
    # Run synchronous example
    run_project()

    # Test dry run
    # test_run_with_dry_run()

    # Run with notifications
    # run_with_notifications()

    # Cancel example
    # cancel_run_example()

    # List recent runs
    # list_recent_runs()
