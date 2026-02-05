#!/usr/bin/env python3
"""
Unit tests for SSHManager module.
"""

import os
from pathlib import Path
from unittest.mock import MagicMock, Mock, call, patch

import paramiko
import pytest

from src.remote.ssh_manager import SSHManager


class TestSSHManager:
    """Test suite for SSHManager class."""

    @pytest.fixture
    def ssh_manager(self, mock_ssh_client):
        """Create an SSHManager instance with mocked SSH client."""
        with patch("src.remote.ssh_manager.paramiko.SSHClient") as mock_client:
            mock_client.return_value = mock_ssh_client
            manager = SSHManager()
            yield manager

    def test_initialization(self):
        """Test SSHManager initialization."""
        with patch("src.remote.ssh_manager.paramiko.SSHClient"):
            manager = SSHManager()
            assert manager is not None
            assert manager.current_host is None
            assert manager.current_user is None

    def test_load_known_hosts_success(self, tmp_path):
        """Test loading known hosts file successfully."""
        known_hosts = tmp_path / ".ssh" / "known_hosts"
        known_hosts.parent.mkdir(parents=True)
        known_hosts.write_text("example.com ssh-rsa AAAAB3NzaC1...\n")

        with patch("os.path.expanduser") as mock_expand:
            mock_expand.return_value = str(known_hosts)
            with patch("src.remote.ssh_manager.paramiko.SSHClient") as mock_client:
                mock_instance = MagicMock()
                mock_client.return_value = mock_instance
                manager = SSHManager()
                mock_instance.load_host_keys.assert_called_once()

    def test_load_known_hosts_missing(self):
        """Test handling missing known hosts file."""
        with patch("os.path.exists") as mock_exists:
            mock_exists.return_value = False
            with patch("src.remote.ssh_manager.paramiko.SSHClient"):
                manager = SSHManager()
                # Should not raise an exception

    def test_connect_basic(self, ssh_manager, mock_ssh_client):
        """Test basic SSH connection."""
        mock_ssh_client.connect.return_value = None

        result = ssh_manager.connect(
            hostname="test.example.com", username="testuser", password="testpass"
        )

        assert result is True
        assert ssh_manager.current_host == "test.example.com"
        assert ssh_manager.current_user == "testuser"
        mock_ssh_client.connect.assert_called_once()

    def test_connect_with_key(self, ssh_manager, mock_ssh_client):
        """Test SSH connection with key file."""
        mock_ssh_client.connect.return_value = None

        result = ssh_manager.connect(
            hostname="test.example.com",
            username="testuser",
            key_filename="/path/to/key",
        )

        assert result is True
        call_args = mock_ssh_client.connect.call_args
        assert call_args[1]["key_filename"] == "/path/to/key"

    def test_connect_with_profile(self, ssh_manager, mock_ssh_client):
        """Test connection using saved profile."""
        # Mock the profile loading
        ssh_manager.config.get_profile = MagicMock(
            return_value={
                "hostname": "192.168.1.100",
                "username": "admin",
                "port": "22",
                "key_file": "/home/user/.ssh/id_rsa",
            }
        )

        mock_ssh_client.connect.return_value = None

        result = ssh_manager.connect(hostname="myserver")

        assert result is True
        assert ssh_manager.current_host == "192.168.1.100"
        assert ssh_manager.current_user == "admin"

    def test_connect_failure(self, ssh_manager, mock_ssh_client):
        """Test handling connection failure."""
        mock_ssh_client.connect.side_effect = Exception("Connection refused")

        result = ssh_manager.connect(hostname="test.example.com", username="testuser")

        assert result is False
        assert ssh_manager.current_host is None

    def test_connect_with_ssh_config(self, ssh_manager, mock_ssh_client):
        """Test connection using SSH config."""
        ssh_manager.config.get_host_config = MagicMock(
            return_value={
                "hostname": "real.example.com",
                "port": 2222,
                "user": "configuser",
                "identityfile": "/path/to/config/key",
            }
        )

        mock_ssh_client.connect.return_value = None

        result = ssh_manager.connect(hostname="myalias")

        assert result is True
        call_args = mock_ssh_client.connect.call_args
        assert call_args[1]["hostname"] == "real.example.com"
        assert call_args[1]["port"] == 2222

    def test_execute_command_success(self, ssh_manager, mock_ssh_client):
        """Test executing command successfully."""
        mock_transport = MagicMock()
        mock_transport.is_active.return_value = True
        mock_ssh_client.get_transport.return_value = mock_transport

        mock_stdout = MagicMock()
        mock_stderr = MagicMock()
        mock_stdout.read.return_value = b"command output"
        mock_stderr.read.return_value = b""
        mock_stdout.channel.recv_exit_status.return_value = 0

        mock_ssh_client.exec_command.return_value = (
            MagicMock(),
            mock_stdout,
            mock_stderr,
        )

        result = ssh_manager.execute_command("ls -la")

        assert result["status"] == 0
        assert result["output"] == "command output"
        assert result["error"] == ""

    def test_execute_command_with_error(self, ssh_manager, mock_ssh_client):
        """Test executing command that returns an error."""
        mock_transport = MagicMock()
        mock_transport.is_active.return_value = True
        mock_ssh_client.get_transport.return_value = mock_transport

        mock_stdout = MagicMock()
        mock_stderr = MagicMock()
        mock_stdout.read.return_value = b""
        mock_stderr.read.return_value = b"command not found"
        mock_stdout.channel.recv_exit_status.return_value = 127

        mock_ssh_client.exec_command.return_value = (
            MagicMock(),
            mock_stdout,
            mock_stderr,
        )

        result = ssh_manager.execute_command("invalidcommand")

        assert result["status"] == 127
        assert result["error"] == "command not found"

    def test_execute_command_not_connected(self, ssh_manager, mock_ssh_client):
        """Test executing command when not connected."""
        mock_ssh_client.get_transport.return_value = None

        result = ssh_manager.execute_command("ls")

        assert result["status"] == -1
        assert "Not connected" in result["error"]

    def test_execute_command_with_sudo(self, ssh_manager, mock_ssh_client):
        """Test executing command with sudo."""
        mock_transport = MagicMock()
        mock_transport.is_active.return_value = True
        mock_ssh_client.get_transport.return_value = mock_transport

        mock_stdout = MagicMock()
        mock_stderr = MagicMock()
        mock_stdout.read.return_value = b"output"
        mock_stderr.read.return_value = b""
        mock_stdout.channel.recv_exit_status.return_value = 0

        mock_ssh_client.exec_command.return_value = (
            MagicMock(),
            mock_stdout,
            mock_stderr,
        )

        ssh_manager.execute_command("apt update", sudo=True)

        call_args = mock_ssh_client.exec_command.call_args
        assert call_args[0][0] == "sudo apt update"

    def test_upload_file_success(self, ssh_manager, mock_ssh_client, mock_scp_client):
        """Test uploading file successfully."""
        mock_transport = MagicMock()
        mock_ssh_client.get_transport.return_value = mock_transport

        with patch("src.remote.ssh_manager.SCPClient") as mock_scp_class:
            mock_scp_class.return_value.__enter__.return_value = mock_scp_client

            result = ssh_manager.upload_file("/local/file.txt", "/remote/file.txt")

            assert result is True
            mock_scp_client.put.assert_called_once()

    def test_upload_file_not_connected(self, ssh_manager, mock_ssh_client):
        """Test uploading file when not connected."""
        mock_ssh_client.get_transport.return_value = None

        result = ssh_manager.upload_file("/local/file.txt", "/remote/file.txt")

        assert result is False

    def test_upload_file_failure(self, ssh_manager, mock_ssh_client, mock_scp_client):
        """Test handling upload failure."""
        mock_transport = MagicMock()
        mock_ssh_client.get_transport.return_value = mock_transport

        with patch("src.remote.ssh_manager.SCPClient") as mock_scp_class:
            mock_scp_instance = MagicMock()
            mock_scp_instance.__enter__.return_value.put.side_effect = Exception(
                "Upload failed"
            )
            mock_scp_class.return_value = mock_scp_instance

            result = ssh_manager.upload_file("/local/file.txt", "/remote/file.txt")

            assert result is False

    def test_download_file_success(self, ssh_manager, mock_ssh_client, mock_scp_client):
        """Test downloading file successfully."""
        mock_transport = MagicMock()
        mock_ssh_client.get_transport.return_value = mock_transport

        with patch("src.remote.ssh_manager.SCPClient") as mock_scp_class:
            mock_scp_class.return_value.__enter__.return_value = mock_scp_client

            result = ssh_manager.download_file("/remote/file.txt", "/local/file.txt")

            assert result is True
            mock_scp_client.get.assert_called_once()

    def test_download_file_not_connected(self, ssh_manager, mock_ssh_client):
        """Test downloading file when not connected."""
        mock_ssh_client.get_transport.return_value = None

        result = ssh_manager.download_file("/remote/file.txt", "/local/file.txt")

        assert result is False

    def test_list_directory(self, ssh_manager, mock_ssh_client):
        """Test listing remote directory."""
        mock_transport = MagicMock()
        mock_transport.is_active.return_value = True
        mock_ssh_client.get_transport.return_value = mock_transport

        ls_output = """total 12
drwxr-xr-x 2 user group 4096 Jan 15 10:00 .
drwxr-xr-x 3 user group 4096 Jan 15 09:00 ..
-rw-r--r-- 1 user group  100 Jan 15 10:00 file.txt
"""
        mock_stdout = MagicMock()
        mock_stderr = MagicMock()
        mock_stdout.read.return_value = ls_output.encode()
        mock_stderr.read.return_value = b""
        mock_stdout.channel.recv_exit_status.return_value = 0

        mock_ssh_client.exec_command.return_value = (
            MagicMock(),
            mock_stdout,
            mock_stderr,
        )

        result = ssh_manager.list_directory("/home/user")

        assert result is True

    def test_create_directory(self, ssh_manager, mock_ssh_client):
        """Test creating remote directory."""
        mock_transport = MagicMock()
        mock_transport.is_active.return_value = True
        mock_ssh_client.get_transport.return_value = mock_transport

        mock_stdout = MagicMock()
        mock_stderr = MagicMock()
        mock_stdout.read.return_value = b""
        mock_stderr.read.return_value = b""
        mock_stdout.channel.recv_exit_status.return_value = 0

        mock_ssh_client.exec_command.return_value = (
            MagicMock(),
            mock_stdout,
            mock_stderr,
        )

        result = ssh_manager.create_directory("/remote/newdir")

        assert result["status"] == 0
        call_args = mock_ssh_client.exec_command.call_args
        assert "mkdir -p" in call_args[0][0]

    def test_remove_file(self, ssh_manager, mock_ssh_client):
        """Test removing remote file."""
        mock_transport = MagicMock()
        mock_transport.is_active.return_value = True
        mock_ssh_client.get_transport.return_value = mock_transport

        mock_stdout = MagicMock()
        mock_stderr = MagicMock()
        mock_stdout.read.return_value = b""
        mock_stderr.read.return_value = b""
        mock_stdout.channel.recv_exit_status.return_value = 0

        mock_ssh_client.exec_command.return_value = (
            MagicMock(),
            mock_stdout,
            mock_stderr,
        )

        result = ssh_manager.remove_file("/remote/file.txt")

        assert result["status"] == 0
        call_args = mock_ssh_client.exec_command.call_args
        assert "rm" in call_args[0][0]

    def test_remove_directory_recursive(self, ssh_manager, mock_ssh_client):
        """Test removing directory recursively."""
        mock_transport = MagicMock()
        mock_transport.is_active.return_value = True
        mock_ssh_client.get_transport.return_value = mock_transport

        mock_stdout = MagicMock()
        mock_stderr = MagicMock()
        mock_stdout.read.return_value = b""
        mock_stderr.read.return_value = b""
        mock_stdout.channel.recv_exit_status.return_value = 0

        mock_ssh_client.exec_command.return_value = (
            MagicMock(),
            mock_stdout,
            mock_stderr,
        )

        result = ssh_manager.remove_file("/remote/dir", recursive=True)

        assert result["status"] == 0
        call_args = mock_ssh_client.exec_command.call_args
        assert "rm -r" in call_args[0][0]

    def test_close_connection(self, ssh_manager, mock_ssh_client):
        """Test closing SSH connection."""
        ssh_manager.current_host = "test.example.com"
        ssh_manager.current_user = "testuser"

        ssh_manager.close()

        mock_ssh_client.close.assert_called_once()
        assert ssh_manager.current_host is None
        assert ssh_manager.current_user is None

    def test_run_script_success(self, ssh_manager, mock_ssh_client, tmp_path):
        """Test running a local script on remote host."""
        script_file = tmp_path / "test_script.sh"
        script_file.write_text("#!/bin/bash\necho 'Hello World'\n")

        mock_transport = MagicMock()
        mock_transport.is_active.return_value = True
        mock_ssh_client.get_transport.return_value = mock_transport

        mock_stdout = MagicMock()
        mock_stderr = MagicMock()
        mock_stdout.read.return_value = b"Hello World"
        mock_stderr.read.return_value = b""
        mock_stdout.channel.recv_exit_status.return_value = 0

        mock_ssh_client.exec_command.return_value = (
            MagicMock(),
            mock_stdout,
            mock_stderr,
        )

        result = ssh_manager.run_script(str(script_file))

        assert result["status"] == 0
        assert result["output"] == "Hello World"

    def test_run_script_not_found(self, ssh_manager):
        """Test running non-existent script."""
        result = ssh_manager.run_script("/nonexistent/script.sh")

        assert result["status"] == -1
        assert "Script not found" in result["error"]

    def test_run_script_with_sudo(self, ssh_manager, mock_ssh_client, tmp_path):
        """Test running script with sudo."""
        script_file = tmp_path / "test_script.sh"
        script_file.write_text("#!/bin/bash\napt update\n")

        mock_transport = MagicMock()
        mock_transport.is_active.return_value = True
        mock_ssh_client.get_transport.return_value = mock_transport

        mock_stdout = MagicMock()
        mock_stderr = MagicMock()
        mock_stdout.read.return_value = b"output"
        mock_stderr.read.return_value = b""
        mock_stdout.channel.recv_exit_status.return_value = 0

        mock_ssh_client.exec_command.return_value = (
            MagicMock(),
            mock_stdout,
            mock_stderr,
        )

        result = ssh_manager.run_script(str(script_file), sudo=True)

        call_args = mock_ssh_client.exec_command.call_args
        assert "sudo" in call_args[0][0]

    def test_interactive_shell_not_connected(self, ssh_manager, mock_ssh_client):
        """Test interactive shell when not connected."""
        mock_ssh_client.get_transport.return_value = None

        # Should handle gracefully
        ssh_manager.interactive_shell()
        # No exception should be raised

    def test_connection_with_custom_port(self, ssh_manager, mock_ssh_client):
        """Test connection with custom port."""
        mock_ssh_client.connect.return_value = None

        result = ssh_manager.connect(
            hostname="test.example.com", username="testuser", port=2222
        )

        assert result is True
        call_args = mock_ssh_client.connect.call_args
        assert call_args[1]["port"] == 2222

    def test_auto_add_policy_set(self):
        """Test that AutoAddPolicy is set on initialization."""
        with patch("src.remote.ssh_manager.paramiko.SSHClient") as mock_client:
            mock_instance = MagicMock()
            mock_client.return_value = mock_instance

            manager = SSHManager()

            mock_instance.set_missing_host_key_policy.assert_called_once()

    def test_execute_command_exception_handling(self, ssh_manager, mock_ssh_client):
        """Test exception handling during command execution."""
        mock_transport = MagicMock()
        mock_transport.is_active.return_value = True
        mock_ssh_client.get_transport.return_value = mock_transport

        mock_ssh_client.exec_command.side_effect = Exception("SSH error")

        result = ssh_manager.execute_command("ls")

        assert result["status"] == -1
        assert "SSH error" in result["error"]
