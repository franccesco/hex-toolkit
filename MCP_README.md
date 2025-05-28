# Hex API MCP (Model Context Protocol) Server

The Hex API SDK includes built-in support for the Model Context Protocol (MCP), allowing you to use Hex functionality directly within Claude Desktop and Claude Code.

## What is MCP?

The Model Context Protocol is an open standard that enables AI assistants like Claude to interact with external tools and data sources. With the Hex API MCP server, Claude can:

- List and search your Hex projects
- Get project details and metadata
- Run Hex projects with parameters
- Monitor run status
- Cancel running projects

## Installation

### Prerequisites

- Python 3.10 or higher
- Hex API key (get one from your Hex workspace settings)
- Claude Desktop and/or Claude Code installed

### Install the SDK

```bash
# Install with MCP support
pip install "hex-api[mcp]"

# Or install with all features
pip install "hex-api[all]"
```

### Set up your API key

```bash
export HEX_API_KEY=your-api-key-here
# Optional: Set custom Hex instance URL
export HEX_API_BASE_URL=https://your-hex-instance.com
```

## Quick Start

### 1. Check Installation Status

```bash
hex mcp status
```

This shows whether the MCP server is configured for Claude Desktop, Claude Code, and your current project.

### 2. Install MCP Server

```bash
# Auto-detect and install for all available Claude applications
hex mcp install

# Install for specific targets
hex mcp install --target claude-desktop
hex mcp install --target claude-code

# Install for Claude Code with specific scope
hex mcp install --target claude-code --scope project  # Share with team via .mcp.json
hex mcp install --target claude-code --scope user     # Available across all projects
hex mcp install --target claude-code --scope local    # Current project only
```

### 3. Restart Claude

After installation:
- **Claude Desktop**: Quit and restart the application
- **Claude Code**: The MCP server is immediately available

### 4. Use Hex in Claude

Look for the 🔧 (tool) icon in Claude and try commands like:
- "List my Hex projects"
- "Run the sales dashboard project"
- "Check the status of my running projects"
- "Search for projects with 'analytics' in the name"

## Available MCP Tools

### `hex_list_projects`
List and search Hex projects with filtering options.

**Parameters:**
- `limit`: Number of results (1-100, default: 25)
- `include_archived`: Include archived projects
- `include_trashed`: Include trashed projects
- `creator_email`: Filter by creator
- `owner_email`: Filter by owner
- `search`: Search projects by name or description

### `hex_get_project`
Get detailed information about a specific project.

**Parameters:**
- `project_id`: The project's unique ID
- `include_sharing`: Include sharing/permission details

### `hex_run_project`
Run a Hex project with optional parameters.

**Parameters:**
- `project_id`: The project's unique ID
- `dry_run`: Perform a dry run
- `update_cache`: Update cached results
- `no_sql_cache`: Skip SQL result cache
- `input_params`: JSON object with input parameters

### `hex_get_run_status`
Check the status of a project run.

**Parameters:**
- `project_id`: The project's unique ID
- `run_id`: The run's unique ID

### `hex_cancel_run`
Cancel a running project.

**Parameters:**
- `project_id`: The project's unique ID
- `run_id`: The run's unique ID

### `hex_list_runs`
List recent runs for a project.

**Parameters:**
- `project_id`: The project's unique ID
- `limit`: Number of results
- `offset`: Skip this many results
- `status_filter`: Filter by status

## Configuration

### Claude Desktop

The installer automatically updates your Claude Desktop configuration at:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

### Claude Code

For Claude Code, you can install at different scopes:

#### User Scope (Default)
Available across all your projects:
```bash
hex mcp install --target claude-code --scope user
```

#### Project Scope
Shared with your team via `.mcp.json`:
```bash
hex mcp install --target claude-code --scope project
```

This creates/updates `.mcp.json` in your project root:
```json
{
  "mcpServers": {
    "hex-api": {
      "command": "hex-api",
      "args": ["mcp", "serve"],
      "env": {
        "HEX_API_KEY": "${HEX_API_KEY}",
        "HEX_API_BASE_URL": "${HEX_API_BASE_URL}"
      }
    }
  }
}
```

#### Local Scope
Available only in the current project:
```bash
hex mcp install --target claude-code --scope local
```

## Advanced Usage

### Running the MCP Server Manually

```bash
# Default stdio transport (for Claude Desktop)
hex mcp serve

# SSE transport for remote access
hex mcp serve --transport sse --port 8080 --host 0.0.0.0
```

### Uninstalling

```bash
# Remove from all detected Claude applications
hex mcp uninstall

# Remove from specific target
hex mcp uninstall --target claude-desktop
hex mcp uninstall --target claude-code --scope project
```

## Troubleshooting

### API Key Not Set
If you see "HEX_API_KEY environment variable not set":
1. Set the environment variable: `export HEX_API_KEY=your-key`
2. Add it to your shell profile (`.bashrc`, `.zshrc`, etc.)
3. For Claude Desktop on macOS, you may need to launch it from Terminal for env vars to work

### Claude Desktop Not Detecting MCP Server
1. Ensure you've restarted Claude Desktop after installation
2. Check the configuration file exists and contains the hex-api entry
3. Run `hex mcp status` to verify installation
4. Check Claude Desktop logs for errors

### Permission Errors
- On Windows, you may need to run the terminal as Administrator
- On macOS/Linux, ensure you have write permissions to the config directories

## Example Workflows

### Daily Report Automation
Tell Claude: "Run my daily sales report project and email me when it's complete"

### Project Discovery
Tell Claude: "Find all projects related to customer analytics that were modified this week"

### Batch Operations
Tell Claude: "Check the status of all my running projects and cancel any that have been running for more than an hour"

## Security

- API keys are stored as environment variables, not in configuration files
- The MCP server runs with your user permissions
- Only install MCP servers from trusted sources
- Project-scoped configurations (`.mcp.json`) should not contain sensitive data

## Contributing

Found a bug or have a feature request? Please open an issue on our GitHub repository.

## License

This MCP server is part of the hex-api SDK and is released under the MIT license.