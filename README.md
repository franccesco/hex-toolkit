# Hex Toolkit

A comprehensive toolkit for working with [Hex](https://hex.tech) - includes Python SDK, CLI, and MCP integration for Claude.

## Features

- 🐍 **Simple, Pythonic interface** - Easy to use with clear method names
- 🔧 **Complete API coverage** - Projects, runs, and more
- 🤖 **MCP Support** - Use Hex directly in Claude Desktop and Claude Code
- 📦 **Minimal dependencies** - Built on httpx for reliability
- 🔐 **Secure** - API key authentication with environment variable support

## Installation

```bash
# Basic installation
pip install hex-toolkit

# With CLI support
pip install "hex-toolkit[cli]"

# With MCP (Model Context Protocol) support
pip install "hex-toolkit[mcp]"

# Install everything
pip install "hex-toolkit[all]"
```

## Quick Start

```python
from hex_toolkit import HexClient

# Initialize the client
client = HexClient(api_key="your-api-key")

# List all projects
projects = client.projects.list()
for project in projects.values:
    print(f"{project.title} - {project.id}")

# Get a specific project
project = client.projects.get("project-id")
print(project.title)

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

## Configuration

The client can be configured via environment variables:

```bash
export HEX_API_KEY="your-api-key"
export HEX_API_BASE_URL="https://app.hex.tech/api"  # Optional
```

Or directly in code:

```python
client = HexClient(
    api_key="your-api-key",
    base_url="https://custom.hex.tech/api",
    timeout=60.0
)
```

## Usage Examples

### Working with Projects

```python
# List projects with filters
projects = client.projects.list(
    limit=50,
    include_archived=False,
    creator_email="user@example.com"
)

# Access project data - fields are converted to snake_case
for project in projects.values:
    print(f"ID: {project.id}")
    print(f"Title: {project.title}")
    print(f"Type: {project.type}")  # ProjectType.PROJECT or ProjectType.COMPONENT
    print(f"Created: {project.created_at}")
    print(f"Last edited: {project.last_edited_at}")
```

### Pagination

```python
# List projects with pagination
after_cursor = None
all_projects = []

while True:
    response = client.projects.list(limit=100, after=after_cursor)
    all_projects.extend(response.values)

    # Check if there are more pages
    after_cursor = response.pagination.after if response.pagination else None
    if not after_cursor:
        break

print(f"Found {len(all_projects)} projects total")
```

### Running Projects

```python
# Simple run
run = client.projects.run("project-id")

# Run with parameters
run = client.projects.run(
    project_id="project-id",
    input_params={
        "date_start": "2024-01-01",
        "date_end": "2024-01-31",
        "metric": "revenue"
    },
    update_published_results=True
)

# Run with notifications
run = client.projects.run(
    project_id="project-id",
    notifications=[{
        "type": "ALL",
        "includeSuccessScreenshot": True,
        "slackChannelIds": ["C0123456789"],
    }]
)
```

### Monitoring Runs

```python
import time

# Wait for completion
run_id = run.run_id
project_id = run.project_id

while True:
    status = client.runs.get_status(project_id, run_id)
    print(f"Status: {status.status}")

    if status.status in ["COMPLETED", "ERRORED", "KILLED"]:
        print(f"Run finished with status: {status.status}")
        if status.elapsed_time:
            print(f"Elapsed time: {status.elapsed_time}ms")
        break

    time.sleep(5)
```

### Error Handling

```python
from hex_toolkit.exceptions import (
    HexAPIError,
    HexAuthenticationError,
    HexNotFoundError,
    HexRateLimitError
)

try:
    project = client.projects.get("invalid-id")
except HexNotFoundError as e:
    print(f"Project not found: {e.message}")
except HexAuthenticationError:
    print("Invalid API key")
except HexRateLimitError as e:
    print(f"Rate limited. Retry after: {e.retry_after} seconds")
except HexAPIError as e:
    print(f"API error: {e.message}")
    print(f"Status code: {e.status_code}")
    print(f"Trace ID: {e.trace_id}")
```

### Creating Embedded URLs

```python
# Create a basic embedded URL
embed = client.embedding.create_presigned_url("project-id")
print(f"Embed URL: {embed.url}")

# Create with options
embed = client.embedding.create_presigned_url(
    project_id="project-id",
    expires_in=300000,  # 5 minutes
    input_parameters={"filter": "Q1"},
    display_options={
        "theme": "dark",
        "noEmbedFooter": True
    }
)
```

## MCP (Model Context Protocol) Support

The SDK includes built-in MCP support for using Hex directly within Claude Desktop and Claude Code. [Learn more about MCP](https://modelcontextprotocol.io).

### Quick Setup

```bash
# Install the MCP server
hex mcp install

# Check installation status
hex mcp status

# Use in Claude - look for the 🔧 icon!
```

See the [MCP documentation](MCP_README.md) for detailed setup and usage instructions.

## API Resources

### Projects

- `client.projects.list(**filters)` - List all projects
- `client.projects.get(project_id)` - Get a specific project
- `client.projects.run(project_id, **options)` - Run a project

### Runs

- `client.runs.get_status(project_id, run_id)` - Get run status
- `client.runs.list(project_id, **filters)` - List runs for a project
- `client.runs.cancel(project_id, run_id)` - Cancel a run

### Embedding

- `client.embedding.create_presigned_url(project_id, **options)` - Create embedded URL

### Semantic Models

- `client.semantic_models.ingest(semantic_model_id, **options)` - Ingest semantic model (Note: File upload support is not yet implemented)

## Response Format

All methods return strongly-typed Pydantic models with convenient dot notation access. The SDK automatically converts the API's camelCase fields to Pythonic snake_case:

```python
# Project object - access with dot notation
project = client.projects.get("project-id")
print(project.id)                # "12345678-1234-1234-1234-123456789012"
print(project.title)             # "Sales Dashboard"
print(project.type)              # ProjectType.PROJECT (enum)
print(project.created_at)        # datetime object (converted from "createdAt")
print(project.last_edited_at)    # datetime object (converted from "lastEditedAt")
print(project.creator.email)     # "user@example.com"
print(project.owner.email)       # "user@example.com"

# Run response - also uses dot notation
run = client.projects.run("project-id")
print(run.project_id)            # "12345678-1234-1234-1234-123456789012"
print(run.run_id)                # "87654321-4321-4321-4321-210987654321"
print(run.run_url)               # "https://app.hex.tech/app/runs/..."
print(run.run_status_url)        # "https://app.hex.tech/api/v1/projects/.../runs/..."

# Paginated responses have a 'values' attribute
projects = client.projects.list()
for project in projects.values:
    print(f"{project.title}: {project.status}")
```

### Field Name Conversion

The API returns camelCase field names, but the SDK automatically converts them to snake_case for a more Pythonic experience:

- `createdAt` → `created_at`
- `lastEditedAt` → `last_edited_at`
- `runId` → `run_id`
- `projectId` → `project_id`
- `inputParams` → `input_params`

### Type Safety

All responses are validated Pydantic models, providing:
- Auto-completion in IDEs
- Type checking with mypy/pyright
- Automatic validation of API responses
- Clear error messages for invalid data

## Development

### Setup

```bash
# Install with development dependencies using uv
uv pip install -e ".[dev]"

# Run tests
uv run pytest

# Run linting
uv run ruff format src tests
uv run ruff check src tests
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/hex_toolkit

# Run specific test file
uv run pytest tests/test_client.py
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request
