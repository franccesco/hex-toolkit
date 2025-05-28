# Hex API CLI

The Hex API SDK includes a command-line interface (CLI) for managing projects and runs directly from your terminal.

## Installation

Install the SDK with CLI dependencies:

```bash
pip install hex-toolkit[cli]
# or with uv
uv pip install hex-toolkit[cli]
```

## Configuration

Set your API key as an environment variable:

```bash
export HEX_API_KEY="your-api-key-here"
```

Optionally, set a custom API base URL:

```bash
export HEX_API_BASE_URL="https://custom.hex.api"
```

## Usage

### General Commands

```bash
# Show help
hex --help

# Show version
hex --version
```

### Project Management

```bash
# List all projects
hex projects list

# List projects with filters
hex projects list --limit 10 --include-archived --creator-email user@example.com

# List projects with custom columns
hex projects list --columns id,name,creator,last_viewed_at,app_views

# Show all available columns
hex projects list --columns id,name,status,owner,created_at,creator,last_viewed_at,app_views

# Search for projects by name or description
hex projects list --search "analytics"

# Search with other filters
hex projects list --search "data" --include-archived --sort -created_at

# Get comprehensive project details
hex projects get PROJECT_ID

# Get project with sharing info
hex projects get PROJECT_ID --include-sharing

# Run a project
hex projects run PROJECT_ID

# Run with options
hex projects run PROJECT_ID --dry-run --wait --poll-interval 10

# Run with cache options
hex projects run PROJECT_ID --update-cache --no-sql-cache

# Run with input parameters
hex projects run PROJECT_ID --input-params '{"param1": "value1", "param2": 123}'
```

### Run Management

```bash
# Get run status
hex runs status PROJECT_ID RUN_ID

# List runs for a project
hex runs list PROJECT_ID

# List runs with filters
hex runs list PROJECT_ID --limit 20 --status COMPLETED

# Cancel a run
hex runs cancel PROJECT_ID RUN_ID

# Cancel without confirmation
hex runs cancel PROJECT_ID RUN_ID --yes
```

## Features

### Rich Terminal Output

The CLI uses Rich for beautiful terminal output including:

- Colored output for better readability
- Progress indicators for long operations
- Formatted tables for list views
- Syntax highlighting for JSON responses

### Auto-completion

The CLI supports shell auto-completion. To enable it:

```bash
hex --install-completion
```

### Custom Columns

The `projects list` command supports customizable columns via the `--columns` option:

**Available columns:**

- `id` - Project ID
- `name` - Project name
- `status` - Project status
- `owner` - Owner email address
- `created_at` - Creation date
- `creator` - Creator email address
- `last_viewed_at` - Last time the project was viewed
- `app_views` - Total number of app views (all time)

**Default columns:** id, name, status, owner, created_at

```bash
# Show only ID and name
hex projects list --columns id,name

# Include creator and analytics data
hex projects list --columns id,name,creator,last_viewed_at,app_views
```

### Search Functionality

The `projects list` command includes a powerful search feature:

```bash
# Search for projects by name or description (case-insensitive)
hex projects list --search "dashboard"

# Combine search with other filters
hex projects list --search "analytics" --include-archived --owner-email data@example.com

# Search with custom sorting
hex projects list --search "report" --sort -last_edited_at

# Search with custom columns
hex projects list --search "metrics" --columns id,name,status,last_viewed_at
```

**Note:** The search feature fetches all available projects and filters them locally. This ensures comprehensive results but may take longer for workspaces with many projects. The progress indicator will show the number of matches found as it searches.

### Pagination

List commands support pagination:

```bash
# Show first 50 projects
hex projects list --limit 50

# List runs with offset
hex runs list PROJECT_ID --limit 10 --offset 20
```

### Error Handling

The CLI provides clear error messages with trace IDs for debugging:

```
[red]API Error: Forbidden: You are not authorized to perform this action. (Status: 403) (Trace ID: abc123)[/red]
```

## Examples

### Running a Project and Waiting for Completion

```bash
# Run a project and wait for it to complete
hex projects run PROJECT_ID --wait --poll-interval 5
```

### Filtering Projects by Owner

```bash
# List all projects owned by a specific user
hex projects list --owner-email owner@example.com --limit 100
```

### Getting Detailed Run Information

```bash
# Get run status with formatted output
hex runs status PROJECT_ID RUN_ID
```

Output:

```
Run Status
Run ID: abc123
Project ID: xyz789
Status: COMPLETED
Started: 2024-01-01T10:00:00
Ended: 2024-01-01T10:05:00
```

### Comprehensive Project Details

The `projects get` command displays all available project information in an organized format:

```bash
hex projects get PROJECT_ID --include-sharing
```

This command shows:

**📋 Basic Information**

- Project ID, type, description
- Status with color coding
- Published version

**👥 People**

- Creator and owner email addresses

**🕐 Timestamps**

- Created, last edited, last published dates
- Archived/trashed dates (if applicable)
- Relative time display (e.g., "2h ago", "yesterday")

**📊 Analytics**

- Last viewed timestamp
- App view counts (all time, 30d, 7d)
- Published results update time

**🏷️ Categories**

- Project categories with descriptions

**✅ Reviews**

- Whether reviews are required

**📅 Schedules**

- Enabled schedules with cadence details
- Schedule timing and timezone info

**🔒 Sharing & Permissions** (with --include-sharing)

- Workspace, public web, and support access levels
- User permissions (first 5 shown)
- Group and collection permissions
- Color-coded access levels (None, App Only, Can View, Can Edit, Full Access)
