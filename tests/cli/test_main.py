"""Tests for main CLI app functionality."""

from unittest.mock import Mock, patch

from hex_toolkit import __version__
from hex_toolkit.cli import app


class TestMainApp:
    """Test main app functionality."""

    def test_version_flag(self, runner):
        """Test --version flag shows version."""
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert f"hex-toolkit version {__version__}" in result.output

    def test_version_flag_short(self, runner):
        """Test -v flag shows version."""
        result = runner.invoke(app, ["-v"])
        assert result.exit_code == 0
        assert f"hex-toolkit version {__version__}" in result.output

    def test_no_command_shows_help(self, runner):
        """Test invoking without command shows help."""
        result = runner.invoke(app, [])
        assert result.exit_code == 0
        assert "Hex API CLI" in result.output
        assert "Commands" in result.output
        assert "projects" in result.output
        assert "runs" in result.output
        assert "mcp" in result.output

    def test_help_flag(self, runner):
        """Test --help flag shows help."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Hex API CLI" in result.output
        assert "Commands" in result.output

    def test_invalid_command(self, runner):
        """Test invalid command shows error."""
        result = runner.invoke(app, ["invalid-command"])
        assert result.exit_code == 2
        assert "No such command" in result.output

    def test_projects_help(self, runner):
        """Test projects --help shows subcommand help."""
        result = runner.invoke(app, ["projects", "--help"])
        assert result.exit_code == 0
        assert "Manage Hex projects" in result.output
        assert "list" in result.output
        assert "get" in result.output
        assert "run" in result.output

    def test_runs_help(self, runner):
        """Test runs --help shows subcommand help."""
        result = runner.invoke(app, ["runs", "--help"])
        assert result.exit_code == 0
        assert "Manage project runs" in result.output
        assert "status" in result.output
        assert "list" in result.output
        assert "cancel" in result.output

    def test_mcp_help(self, runner):
        """Test mcp --help shows subcommand help."""
        result = runner.invoke(app, ["mcp", "--help"])
        assert result.exit_code == 0
        assert "MCP (Model Context Protocol)" in result.output
        assert "serve" in result.output
        assert "install" in result.output
        assert "uninstall" in result.output
        assert "status" in result.output


class TestEnvironmentHandling:
    """Test environment variable handling."""

    def test_missing_api_key_error(self, runner, mock_env_no_api_key):  # noqa: ARG002
        """Test error when HEX_API_KEY is missing."""
        result = runner.invoke(app, ["projects", "list"])
        assert result.exit_code == 1
        assert "HEX_API_KEY environment variable not set" in result.output

    def test_api_key_from_env(self, runner, mock_env_api_key, mock_hex_client):  # noqa: ARG002
        """Test API key is read from environment."""
        mock_hex_client.projects.list.return_value = Mock(values=[], pagination=None)

        result = runner.invoke(app, ["projects", "list"])
        # Should not error about missing key
        assert "HEX_API_KEY environment variable not set" not in result.output

    def test_base_url_from_env(self, runner, mock_env_api_key, monkeypatch):  # noqa: ARG002
        """Test HEX_API_BASE_URL is used when set."""
        monkeypatch.setenv("HEX_API_BASE_URL", "https://custom.hex.tech/api")

        with patch("hex_toolkit.cli.HexClient") as mock_client_class:
            mock_client_class.return_value = Mock()
            runner.invoke(app, ["projects", "list"])

            # Verify custom base URL was passed
            mock_client_class.assert_called_with(
                api_key="test-api-key",
                base_url="https://custom.hex.tech/api"
            )

