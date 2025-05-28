"""MCP server installer for Claude Desktop and Claude Code."""

import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

from .config import (
    add_to_project_mcp_config,
    find_project_root,
    load_mcp_config,
    remove_from_project_mcp_config,
)

console = Console()


class MCPInstaller:
    """Handles installation of Hex Toolkit MCP server for Claude Desktop and Claude Code."""

    def __init__(self):
        self.system = platform.system()
        self.claude_desktop_config_path = self._get_claude_desktop_config_path()
        self.is_claude_code_available = self._check_claude_code()

    def _get_claude_desktop_config_path(self) -> Path | None:
        """Get the Claude Desktop configuration file path based on OS."""
        if self.system == "Darwin":  # macOS
            path = (
                Path.home()
                / "Library"
                / "Application Support"
                / "Claude"
                / "claude_desktop_config.json"
            )
        elif self.system == "Windows":
            path = (
                Path(os.environ.get("APPDATA", ""))
                / "Claude"
                / "claude_desktop_config.json"
            )
        elif self.system == "Linux":
            path = Path.home() / ".config" / "Claude" / "claude_desktop_config.json"
        else:
            return None

        return path if path.parent.exists() else None

    def _check_claude_code(self) -> bool:
        """Check if Claude Code CLI is available."""
        try:
            result = subprocess.run(
                ["claude", "--version"], capture_output=True, text=True, timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def _get_hex_toolkit_command_claude_desktop(self) -> list[str]:
        """Get the command to run hex MCP server for Claude Desktop (needs absolute paths)."""
        # Check if hex is installed in PATH
        hex_path = shutil.which("hex")

        if hex_path:
            return [hex_path, "mcp", "serve"]
        else:
            # Fallback to Python module execution with absolute path
            return [sys.executable, "-m", "hex_toolkit.cli", "mcp", "serve"]

    def _get_hex_toolkit_command_claude_code(self) -> list[str]:
        """Get the command to run hex MCP server for Claude Code (can use relative paths)."""
        # Check if hex is installed in PATH
        hex_toolkit_in_path = shutil.which("hex") is not None

        if hex_toolkit_in_path:
            return ["hex", "mcp", "serve"]
        else:
            # Fallback to Python module execution
            return [sys.executable, "-m", "hex_toolkit.cli", "mcp", "serve"]

    def _read_claude_desktop_config(self) -> dict[str, Any]:
        """Read Claude Desktop configuration."""
        if (
            not self.claude_desktop_config_path
            or not self.claude_desktop_config_path.exists()
        ):
            return {}

        try:
            with open(self.claude_desktop_config_path) as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            return {}

    def _write_claude_desktop_config(self, config: dict[str, Any]) -> None:
        """Write Claude Desktop configuration."""
        if not self.claude_desktop_config_path:
            raise ValueError("Claude Desktop configuration path not found")

        # Create directory if it doesn't exist
        self.claude_desktop_config_path.parent.mkdir(parents=True, exist_ok=True)

        # Write config with pretty formatting
        with open(self.claude_desktop_config_path, "w") as f:
            json.dump(config, f, indent=2)

    def _backup_config(self, path: Path) -> Path | None:
        """Create a backup of the configuration file."""
        if not path.exists():
            return None

        backup_path = path.with_suffix(".json.backup")
        shutil.copy2(path, backup_path)
        return backup_path

    def _install_claude_desktop(self, force: bool = False) -> bool:
        """Install MCP server for Claude Desktop."""
        console.print("\n[cyan]Installing for Claude Desktop...[/cyan]")

        if not self.claude_desktop_config_path:
            console.print(
                "[yellow]Claude Desktop configuration path not found[/yellow]"
            )
            return False

        # Read existing config
        config = self._read_claude_desktop_config()

        # Check if already installed
        if (
            "mcpServers" in config
            and "hex-toolkit" in config["mcpServers"]
            and not force
        ):
            console.print(
                "[yellow]Hex Toolkit MCP server already configured in Claude Desktop[/yellow]"
            )
            if not Confirm.ask("Do you want to update the configuration?"):
                return False

        # Prompt for API key since Claude Desktop can't access environment variables
        api_key = os.getenv("HEX_API_KEY")
        if not api_key:
            console.print(
                "\n[yellow]Claude Desktop cannot access environment variables.[/yellow]"
            )
            console.print(
                "Please provide your Hex API key to configure the MCP server."
            )
            api_key = Prompt.ask("Enter your Hex API key", password=True)
            if not api_key or not api_key.strip():
                console.print(
                    "[red]API key is required for Claude Desktop configuration[/red]"
                )
                return False

        # Get base URL (optional)
        base_url = os.getenv("HEX_API_BASE_URL", "https://api.hex.tech")

        # Backup existing config
        if self.claude_desktop_config_path.exists():
            backup_path = self._backup_config(self.claude_desktop_config_path)
            if backup_path:
                console.print(f"[dim]Backed up existing config to: {backup_path}[/dim]")

        # Initialize mcpServers if not present
        if "mcpServers" not in config:
            config["mcpServers"] = {}

        # Add hex-toolkit server configuration with actual API key
        command = self._get_hex_toolkit_command_claude_desktop()
        config["mcpServers"]["hex-toolkit"] = {
            "command": command[0],
            "args": command[1:],
            "env": {
                "HEX_API_KEY": api_key,
                "HEX_API_BASE_URL": base_url,
            },
        }

        # Write updated config
        self._write_claude_desktop_config(config)
        console.print(f"[green]✓[/green] Updated: {self.claude_desktop_config_path}")

        return True

    def _install_claude_code(self, scope: str = "user", force: bool = False) -> bool:  # noqa: ARG002
        """Install MCP server for Claude Code."""
        console.print("\n[cyan]Installing for Claude Code...[/cyan]")

        if not self.is_claude_code_available:
            console.print("[yellow]Claude Code CLI not found[/yellow]")
            return False

        # For project scope, use .mcp.json instead
        if scope == "project":
            return self._install_project_config()

        # Build the claude mcp add command
        command = self._get_hex_toolkit_command_claude_code()
        claude_cmd = [
            "claude",
            "mcp",
            "add",
            "hex-toolkit",  # server name
            command[0],  # command
            *command[1:],  # args
            "-e",
            f"HEX_API_KEY={os.getenv('HEX_API_KEY', '${HEX_API_KEY}')}",
        ]

        # Add base URL if set
        base_url = os.getenv("HEX_API_BASE_URL")
        if base_url:
            claude_cmd.extend(["-e", f"HEX_API_BASE_URL={base_url}"])

        # Add scope for non-user installations
        if scope == "local":
            claude_cmd.extend(["--scope", "local"])

        # Execute the command
        try:
            result = subprocess.run(claude_cmd, capture_output=True, text=True)
            if result.returncode == 0:
                console.print(
                    f"[green]✓[/green] Installed Hex API MCP server in Claude Code ({scope} scope)"
                )
                return True
            else:
                console.print(f"[red]Failed to install:[/red] {result.stderr}")
                return False
        except Exception as e:
            console.print(f"[red]Error running claude command:[/red] {e}")
            return False

    def _install_project_config(self) -> bool:
        """Install MCP server configuration in project's .mcp.json."""
        project_root = find_project_root()
        if not project_root:
            console.print(
                "[red]Could not find project root (no .git or pyproject.toml)[/red]"
            )
            return False

        mcp_path = project_root / ".mcp.json"

        # Check if already exists
        existing_config = load_mcp_config(mcp_path)
        if existing_config.get("mcpServers", {}).get("hex-toolkit"):
            console.print(
                "[yellow]Hex Toolkit already configured in .mcp.json[/yellow]"
            )
            if not Confirm.ask("Do you want to update the configuration?"):
                return False

        # Add configuration
        if add_to_project_mcp_config():
            console.print(f"[green]✓[/green] Added Hex Toolkit to {mcp_path}")
            console.print(
                "[dim]This configuration will be available to all team members[/dim]"
            )
            return True
        else:
            console.print("[red]Failed to update .mcp.json[/red]")
            return False

    def _check_api_key(self) -> bool:
        """Check if HEX_API_KEY is set."""
        api_key = os.getenv("HEX_API_KEY")
        if not api_key:
            console.print(
                "\n[yellow]Warning: HEX_API_KEY environment variable is not set[/yellow]"
            )
            console.print("You'll need to set it before using the MCP server:")
            console.print("  export HEX_API_KEY=your-api-key")
            return False
        return True

    def install(
        self, target: str = "auto", scope: str = "user", force: bool = False
    ) -> None:
        """Install the Hex API MCP server."""
        console.print(
            Panel(
                "[bold]🚀 Hex Toolkit MCP Server Installation[/bold]\n\n"
                "This will configure the Hex Toolkit MCP server for use with Claude",
                expand=False,
            )
        )

        # Check API key
        self._check_api_key()

        # Detect available targets
        targets = []
        if target == "auto":
            if self.claude_desktop_config_path:
                targets.append("claude-desktop")
            if self.is_claude_code_available:
                targets.append("claude-code")

            if not targets:
                console.print("[red]No Claude installations detected[/red]")
                return

            console.print("\nDetected environments:")
            if "claude-desktop" in targets:
                console.print("[green]✓[/green] Claude Desktop")
            if "claude-code" in targets:
                console.print("[green]✓[/green] Claude Code")
        elif target == "all":
            targets = ["claude-desktop", "claude-code"]
        else:
            targets = [target]

        # Install for each target
        success = []
        for t in targets:
            if t == "claude-desktop" and self.claude_desktop_config_path:
                if self._install_claude_desktop(force):
                    success.append("Claude Desktop")
            elif (
                t == "claude-code"
                and self.is_claude_code_available
                and self._install_claude_code(scope, force)
            ):
                success.append(f"Claude Code ({scope})")

        # Show summary
        if success:
            console.print("\n[green]✓ Installation complete![/green]")
            console.print("\n[bold]Next steps:[/bold]")
            if "Claude Desktop" in success:
                console.print("• Restart Claude Desktop")
            console.print("• Look for the 🔧 icon to access Hex tools")
            console.print('• Try: "List my Hex projects"')

            if not os.getenv("HEX_API_KEY"):
                console.print(
                    "\n[yellow]Remember to set your HEX_API_KEY environment variable![/yellow]"
                )
        else:
            console.print("\n[red]Installation failed[/red]")

    def uninstall(self, target: str = "auto", scope: str = "user") -> None:
        """Uninstall the Hex API MCP server."""
        console.print(
            Panel("[bold]🗑️  Hex Toolkit MCP Server Uninstallation[/bold]", expand=False)
        )

        # Detect targets
        targets = []
        if target == "auto":
            if self.claude_desktop_config_path:
                config = self._read_claude_desktop_config()
                if config.get("mcpServers", {}).get("hex-toolkit"):
                    targets.append("claude-desktop")
            if self.is_claude_code_available:
                targets.append("claude-code")
        elif target == "all":
            targets = ["claude-desktop", "claude-code"]
        else:
            targets = [target]

        # Uninstall from each target
        for t in targets:
            if t == "claude-desktop":
                self._uninstall_claude_desktop()
            elif t == "claude-code":
                self._uninstall_claude_code(scope)

    def _uninstall_claude_desktop(self) -> None:
        """Remove MCP server from Claude Desktop."""
        if not self.claude_desktop_config_path:
            return

        config = self._read_claude_desktop_config()
        if "mcpServers" in config and "hex-toolkit" in config["mcpServers"]:
            # Backup before removing
            backup_path = self._backup_config(self.claude_desktop_config_path)
            if backup_path:
                console.print(f"[dim]Backed up config to: {backup_path}[/dim]")

            del config["mcpServers"]["hex-toolkit"]

            # Remove empty mcpServers object
            if not config["mcpServers"]:
                del config["mcpServers"]

            self._write_claude_desktop_config(config)
            console.print("[green]✓[/green] Removed from Claude Desktop")
        else:
            console.print(
                "[yellow]Hex Toolkit not configured in Claude Desktop[/yellow]"
            )

    def _uninstall_claude_code(self, scope: str = "user") -> None:
        """Remove MCP server from Claude Code."""
        if scope == "project":
            # Remove from .mcp.json
            if remove_from_project_mcp_config():
                console.print("[green]✓[/green] Removed from project .mcp.json")
            else:
                console.print("[yellow]Could not remove from .mcp.json[/yellow]")
            return

        if not self.is_claude_code_available:
            return

        cmd = ["claude", "mcp", "remove", "hex-toolkit"]
        if scope == "local":
            cmd.extend(["--scope", "local"])

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                console.print(f"[green]✓[/green] Removed from Claude Code ({scope})")
            else:
                console.print(
                    f"[yellow]Could not remove from Claude Code: {result.stderr}[/yellow]"
                )
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")

    def status(self) -> None:
        """Check installation status."""
        console.print(
            Panel("[bold]📊 Hex Toolkit MCP Server Status[/bold]", expand=False)
        )

        table = Table(show_header=True)
        table.add_column("Environment", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Details")

        # Check Claude Desktop
        if self.claude_desktop_config_path:
            config = self._read_claude_desktop_config()
            if config.get("mcpServers", {}).get("hex-toolkit"):
                status = "[green]Installed[/green]"
                details = f"Config: {self.claude_desktop_config_path}"
            else:
                status = "[dim]Not installed[/dim]"
                details = "Run: hex mcp install --target claude-desktop"
        else:
            status = "[red]Not found[/red]"
            details = "Claude Desktop not detected"

        table.add_row("Claude Desktop", status, details)

        # Check Claude Code
        if self.is_claude_code_available:
            # Try to list MCP servers
            try:
                result = subprocess.run(
                    ["claude", "mcp", "list"], capture_output=True, text=True
                )
                if "hex-toolkit" in result.stdout:
                    status = "[green]Installed[/green]"
                    details = "Run: claude mcp list"
                else:
                    status = "[dim]Not installed[/dim]"
                    details = "Run: hex mcp install --target claude-code"
            except Exception:
                status = "[yellow]Unknown[/yellow]"
                details = "Could not check status"
        else:
            status = "[red]Not found[/red]"
            details = "Claude Code CLI not detected"

        table.add_row("Claude Code", status, details)

        # Check project configuration
        project_root = find_project_root()
        if project_root:
            mcp_path = project_root / ".mcp.json"
            if mcp_path.exists():
                config = load_mcp_config(mcp_path)
                if config.get("mcpServers", {}).get("hex-toolkit"):
                    status = "[green]Configured[/green]"
                    details = f"Config: {mcp_path}"
                else:
                    status = "[dim]Not configured[/dim]"
                    details = "Run: hex mcp install --scope project"
            else:
                status = "[dim]Not found[/dim]"
                details = "Run: hex mcp install --scope project"
        else:
            status = "[yellow]No project[/yellow]"
            details = "Not in a project directory"

        table.add_row("Project Config", status, details)

        # Check API key
        api_key = os.getenv("HEX_API_KEY")
        if api_key:
            key_display = f"{api_key[:8]}..." if len(api_key) > 8 else "Set"
            status = "[green]Set[/green]"
            details = f"Key: {key_display}"
        else:
            status = "[red]Not set[/red]"
            details = "export HEX_API_KEY=your-key"

        table.add_row("HEX_API_KEY", status, details)

        console.print(table)
