"""MCP configuration utilities for project-scoped settings."""

import json
from pathlib import Path
from typing import Any


def find_project_root(start_path: Path | None = None) -> Path | None:
    """Find the project root by looking for .git or pyproject.toml."""
    current = Path(start_path) if start_path else Path.cwd()

    while current != current.parent:
        if (current / ".git").exists() or (current / "pyproject.toml").exists():
            return current
        current = current.parent

    return None


def load_mcp_config(path: Path | None = None) -> dict[str, Any]:
    """Load .mcp.json configuration from project root."""
    if not path:
        project_root = find_project_root()
        if not project_root:
            return {}
        path = project_root / ".mcp.json"

    if not path.exists():
        return {}

    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}


def save_mcp_config(config: dict[str, Any], path: Path | None = None) -> None:
    """Save .mcp.json configuration to project root."""
    if not path:
        project_root = find_project_root()
        if not project_root:
            raise ValueError("Could not find project root")
        path = project_root / ".mcp.json"

    with open(path, "w") as f:
        json.dump(config, f, indent=2)
        f.write("\n")  # Add newline at end of file


def get_hex_toolkit_mcp_config() -> dict[str, Any]:
    """Get the Hex Toolkit MCP server configuration for .mcp.json."""
    return {
        "mcpServers": {
            "hex-toolkit": {
                "command": "hex",
                "args": ["mcp", "serve"],
                "env": {
                    "HEX_API_KEY": "${HEX_API_KEY}",
                    "HEX_API_BASE_URL": "${HEX_API_BASE_URL}",
                },
            }
        }
    }


def add_to_project_mcp_config() -> bool:
    """Add Hex Toolkit to project's .mcp.json file."""
    config = load_mcp_config()

    # Initialize mcpServers if not present
    if "mcpServers" not in config:
        config["mcpServers"] = {}

    # Add hex-toolkit server configuration
    config["mcpServers"]["hex-toolkit"] = {
        "command": "hex",
        "args": ["mcp", "serve"],
        "env": {
            "HEX_API_KEY": "${HEX_API_KEY}",
            "HEX_API_BASE_URL": "${HEX_API_BASE_URL}",
        },
    }

    # Save back
    try:
        save_mcp_config(config)
        return True
    except Exception:
        return False


def remove_from_project_mcp_config() -> bool:
    """Remove Hex Toolkit from project's .mcp.json file."""
    config = load_mcp_config()

    if "mcpServers" in config and "hex-toolkit" in config["mcpServers"]:
        del config["mcpServers"]["hex-toolkit"]

        # Remove empty mcpServers
        if not config["mcpServers"]:
            del config["mcpServers"]

        # Save back (or delete if empty)
        try:
            if config:
                save_mcp_config(config)
            else:
                # Delete empty config file
                project_root = find_project_root()
                if project_root:
                    mcp_path = project_root / ".mcp.json"
                    if mcp_path.exists():
                        mcp_path.unlink()
            return True
        except Exception:
            return False

    return True  # Already not in config
