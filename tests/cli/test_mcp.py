"""Tests for MCP-related CLI commands."""

from unittest.mock import Mock, patch

from hex_toolkit.cli import app


class TestMCPServe:
    """Test 'hex mcp serve' command."""

    def test_serve_stdio_default(self, runner, mock_env_api_key):  # noqa: ARG002
        """Test MCP serve with default stdio transport."""
        with patch("hex_toolkit.mcp.mcp_server.run") as mock_run:
            result = runner.invoke(app, ["mcp", "serve"])

            assert result.exit_code == 0
            mock_run.assert_called_once_with()

    def test_serve_stdio_explicit(self, runner, mock_env_api_key):  # noqa: ARG002
        """Test MCP serve with explicit stdio transport."""
        with patch("hex_toolkit.mcp.mcp_server.run") as mock_run:
            result = runner.invoke(app, ["mcp", "serve", "--transport", "stdio"])

            assert result.exit_code == 0
            mock_run.assert_called_once_with()

    def test_serve_sse_transport(self, runner, mock_env_api_key):  # noqa: ARG002
        """Test MCP serve with SSE transport."""
        with patch("hex_toolkit.mcp.mcp_server.run") as mock_run:
            result = runner.invoke(app, [
                "mcp", "serve",
                "--transport", "sse",
                "--port", "9090",
                "--host", "0.0.0.0"
            ])

            assert result.exit_code == 0
            assert "Starting Hex Toolkit MCP server (SSE transport)" in result.output
            mock_run.assert_called_once_with(
                transport="sse",
                sse_host="0.0.0.0",
                sse_port=9090
            )

    def test_serve_missing_api_key(self, runner, mock_env_no_api_key):  # noqa: ARG002
        """Test MCP serve fails without API key."""
        result = runner.invoke(app, ["mcp", "serve"])

        assert result.exit_code == 1
        # For stdio transport, error should not be printed to stdout

    def test_serve_invalid_transport(self, runner, mock_env_api_key):  # noqa: ARG002
        """Test MCP serve with invalid transport."""
        result = runner.invoke(app, ["mcp", "serve", "--transport", "invalid"])

        assert result.exit_code == 1
        assert "Unknown transport: invalid" in result.output

    def test_serve_keyboard_interrupt_stdio(self, runner, mock_env_api_key):  # noqa: ARG002
        """Test handling keyboard interrupt for stdio transport."""
        with patch("hex_toolkit.mcp.mcp_server.run") as mock_run:
            mock_run.side_effect = KeyboardInterrupt()

            result = runner.invoke(app, ["mcp", "serve", "--transport", "stdio"])

            assert result.exit_code == 0
            # No output for stdio transport

    def test_serve_keyboard_interrupt_sse(self, runner, mock_env_api_key):  # noqa: ARG002
        """Test handling keyboard interrupt for SSE transport."""
        with patch("hex_toolkit.mcp.mcp_server.run") as mock_run:
            mock_run.side_effect = KeyboardInterrupt()

            result = runner.invoke(app, ["mcp", "serve", "--transport", "sse"])

            assert result.exit_code == 0
            assert "MCP server stopped" in result.output

    def test_serve_general_error(self, runner, mock_env_api_key):  # noqa: ARG002
        """Test handling of general errors during serve."""
        with patch("hex_toolkit.mcp.mcp_server.run") as mock_run:
            mock_run.side_effect = Exception("Server error")

            result = runner.invoke(app, ["mcp", "serve", "--transport", "sse"])

            assert result.exit_code == 1
            assert "Server error" in result.output


class TestMCPInstall:
    """Test 'hex mcp install' command."""

    def test_install_auto(self, runner, mock_env_api_key):  # noqa: ARG002
        """Test MCP install with auto target."""
        with patch("hex_toolkit.mcp.installer.MCPInstaller") as mock_installer_class:
            mock_installer = Mock()
            mock_installer_class.return_value = mock_installer

            result = runner.invoke(app, ["mcp", "install"])

            assert result.exit_code == 0
            mock_installer.install.assert_called_once_with(
                target="auto",
                scope="user",
                force=False
            )

    def test_install_specific_target(self, runner, mock_env_api_key):  # noqa: ARG002
        """Test MCP install with specific target."""
        with patch("hex_toolkit.mcp.installer.MCPInstaller") as mock_installer_class:
            mock_installer = Mock()
            mock_installer_class.return_value = mock_installer

            result = runner.invoke(app, [
                "mcp", "install",
                "--target", "claude-desktop",
                "--scope", "project",
                "--force"
            ])

            assert result.exit_code == 0
            mock_installer.install.assert_called_once_with(
                target="claude-desktop",
                scope="project",
                force=True
            )

    def test_install_all_targets(self, runner, mock_env_api_key):  # noqa: ARG002
        """Test MCP install with all targets."""
        with patch("hex_toolkit.mcp.installer.MCPInstaller") as mock_installer_class:
            mock_installer = Mock()
            mock_installer_class.return_value = mock_installer

            result = runner.invoke(app, ["mcp", "install", "--target", "all"])

            assert result.exit_code == 0
            mock_installer.install.assert_called_once_with(
                target="all",
                scope="user",
                force=False
            )

    def test_install_error(self, runner, mock_env_api_key):  # noqa: ARG002
        """Test handling of installation errors."""
        with patch("hex_toolkit.mcp.installer.MCPInstaller") as mock_installer_class:
            mock_installer = Mock()
            mock_installer.install.side_effect = Exception("Installation failed")
            mock_installer_class.return_value = mock_installer

            result = runner.invoke(app, ["mcp", "install"])

            assert result.exit_code == 1
            assert "Installation failed" in result.output


class TestMCPUninstall:
    """Test 'hex mcp uninstall' command."""

    def test_uninstall_auto(self, runner, mock_env_api_key):  # noqa: ARG002
        """Test MCP uninstall with auto target."""
        with patch("hex_toolkit.mcp.installer.MCPInstaller") as mock_installer_class:
            mock_installer = Mock()
            mock_installer_class.return_value = mock_installer

            result = runner.invoke(app, ["mcp", "uninstall"])

            assert result.exit_code == 0
            mock_installer.uninstall.assert_called_once_with(
                target="auto",
                scope="user"
            )

    def test_uninstall_specific_target(self, runner, mock_env_api_key):  # noqa: ARG002
        """Test MCP uninstall with specific target."""
        with patch("hex_toolkit.mcp.installer.MCPInstaller") as mock_installer_class:
            mock_installer = Mock()
            mock_installer_class.return_value = mock_installer

            result = runner.invoke(app, [
                "mcp", "uninstall",
                "--target", "claude-code",
                "--scope", "local"
            ])

            assert result.exit_code == 0
            mock_installer.uninstall.assert_called_once_with(
                target="claude-code",
                scope="local"
            )

    def test_uninstall_error(self, runner, mock_env_api_key):  # noqa: ARG002
        """Test handling of uninstallation errors."""
        with patch("hex_toolkit.mcp.installer.MCPInstaller") as mock_installer_class:
            mock_installer = Mock()
            mock_installer.uninstall.side_effect = Exception("Uninstallation failed")
            mock_installer_class.return_value = mock_installer

            result = runner.invoke(app, ["mcp", "uninstall"])

            assert result.exit_code == 1
            assert "Uninstallation failed" in result.output


class TestMCPStatus:
    """Test 'hex mcp status' command."""

    def test_status_check(self, runner, mock_env_api_key):  # noqa: ARG002
        """Test MCP status check."""
        with patch("hex_toolkit.mcp.installer.MCPInstaller") as mock_installer_class:
            mock_installer = Mock()
            mock_installer_class.return_value = mock_installer

            result = runner.invoke(app, ["mcp", "status"])

            assert result.exit_code == 0
            mock_installer.status.assert_called_once_with()

    def test_status_error(self, runner, mock_env_api_key):  # noqa: ARG002
        """Test handling of status check errors."""
        with patch("hex_toolkit.mcp.installer.MCPInstaller") as mock_installer_class:
            mock_installer = Mock()
            mock_installer.status.side_effect = Exception("Status check failed")
            mock_installer_class.return_value = mock_installer

            result = runner.invoke(app, ["mcp", "status"])

            assert result.exit_code == 1
            assert "Status check failed" in result.output
