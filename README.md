# Hex Python SDK

A Python SDK for interacting with the [Hex API](https://hex.tech).

## Installation

```bash
pip install hex-api
```

## Quick Start

```python
from hex_api import HexClient

# Initialize the client
client = HexClient(api_key="your-api-key")

# List all projects
projects = client.projects.list()
for project in projects.values:
    print(f"{project.title} - {project.id}")

# Get a specific project
project = client.projects.get("project-id")

# Run a project
run = client.projects.run(
    project_id="project-id",
    input_params={"param1": "value1"}
)
print(f"Run started: {run.run_id}")

# Check run status
status = client.runs.get_status(project_id="project-id", run_id=run.run_id)
print(f"Status: {status.status}")
```

## Features

- **Type-safe**: Full type hints and Pydantic models
- **Comprehensive**: Covers all Hex API endpoints
- **Developer-friendly**: Clear error messages and intuitive API
- **Configurable**: Easy configuration via environment variables

## Configuration

The client can be configured via environment variables:

```bash
export HEX_API_KEY="your-api-key"
export HEX_API_BASE_URL="https://app.hex.tech/api"  # Optional
```

## Usage Examples

### List Projects with Pagination

```python
# List projects with pagination
projects = client.projects.list(limit=10)
while projects.pagination.after:
    print(f"Processing {len(projects.values)} projects...")
    projects = client.projects.list(after=projects.pagination.after)
```

### Run Project with Notifications

```python
# Run with Slack notifications
run = client.projects.run(
    project_id="project-id",
    notifications=[{
        "type": "ALL",
        "includeSuccessScreenshot": True,
        "slackChannelIds": ["C0123456789"],
    }]
)
```

### Monitor Run Status

```python
import time

# Wait for completion
while True:
    status = client.runs.get_status(project_id, run.run_id)
    if status.status in ["COMPLETED", "ERRORED", "KILLED"]:
        break
    print(f"Status: {status.status}")
    time.sleep(5)
```

### Error Handling

```python
from hex_api.exceptions import HexAPIError, HexAuthenticationError

try:
    project = client.projects.get("invalid-id")
except HexAuthenticationError:
    print("Invalid API key")
except HexAPIError as e:
    print(f"API error: {e.message}")
    print(f"Trace ID: {e.trace_id}")
```

## API Resources

### Projects
- `client.projects.list()` - List all projects
- `client.projects.get(project_id)` - Get a specific project
- `client.projects.run(project_id, **options)` - Run a project

### Runs
- `client.runs.get_status(project_id, run_id)` - Get run status
- `client.runs.list(project_id)` - List runs for a project
- `client.runs.cancel(project_id, run_id)` - Cancel a run

### Embedding
- `client.embedding.create_presigned_url(project_id, **options)` - Create embedded URL

### Semantic Models
- `client.semantic_models.ingest(semantic_model_id, **options)` - Ingest semantic model

## Development

### Setup

```bash
# Install with development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
black src tests
ruff check src tests

# Type checking
mypy src
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.