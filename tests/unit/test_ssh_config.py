#!/usr/bin/env python3
"""
Unit tests for SSHConfig module.
"""

import configparser
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest

from src.remote.ssh_config import SSHConfig


class TestSSHConfig:
    """Test suite for SSHConfig class."""

    @pytest.fixture
    def ssh_config(self, ssh_config_dir, opszen_config_dir):
        """Create an SSHConfig instance with mocked directories."""
        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = ssh_config_dir.parent

            # Ensure .opszen directory exists
            opszen_dir = ssh_config_dir.parent / ".opszen"
            opszen_dir.mkdir(exist_ok=True)

            config = SSHConfig()
            yield config

    def test_initialization(self):
        """Test SSHConfig initialization."""
        with patch("pathlib.Path.home") as mock_home, patch(
            "pathlib.Path.exists"
        ) as mock_exists:
            mock_home.return_value = Path("/home/test")
            mock_exists.return_value = False

            config = SSHConfig()
            assert config is not None
            assert config.config is not None
            assert config.profiles is not None

    def test_load_ssh_config_success(self, ssh_config_dir):
        """Test loading SSH config file successfully."""
        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = ssh_config_dir.parent
            config = SSHConfig()

            # Should load config without errors
            assert config.config is not None

    def test_load_ssh_config_missing(self):
        """Test handling missing SSH config file."""
        with patch("pathlib.Path.home") as mock_home, patch(
            "pathlib.Path.exists"
        ) as mock_exists:
            mock_home.return_value = Path("/home/test")
            mock_exists.return_value = False

            # Should not raise exception
            config = SSHConfig()
            assert config is not None

    def test_load_ssh_config_parse_error(self):
        """Test handling SSH config parse error."""
        with patch("pathlib.Path.home") as mock_home, patch(
            "pathlib.Path.exists"
        ) as mock_exists, patch(
            "builtins.open", mock_open(read_data="invalid config data")
        ):
            mock_home.return_value = Path("/home/test")
            mock_exists.return_value = True

            # Should handle parse error gracefully
            config = SSHConfig()
            assert config is not None

    def test_load_profiles_success(self, opszen_config_dir):
        """Test loading connection profiles successfully."""
        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = opszen_config_dir.parent
            config = SSHConfig()

            assert len(config.profiles) > 0
            assert "myserver" in config.profiles

    def test_load_profiles_missing(self):
        """Test handling missing profiles file."""
        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = Path("/home/test")
            config = SSHConfig()

            # Should have empty profiles
            assert config.profiles == {}

    def test_get_host_config_found(self, ssh_config_dir):
        """Test getting host config for known host."""
        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = ssh_config_dir.parent
            config = SSHConfig()

            host_config = config.get_host_config("testhost")

            assert host_config["hostname"] == "192.168.1.100"
            assert host_config["port"] == 22
            assert host_config["user"] == "testuser"

    def test_get_host_config_not_found(self):
        """Test getting host config for unknown host."""
        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = Path("/home/test")
            config = SSHConfig()

            host_config = config.get_host_config("unknownhost")

            assert host_config["hostname"] == "unknownhost"
            assert host_config["port"] == 22
            assert host_config["user"] is None
            assert host_config["identityfile"] is None

    def test_get_host_config_with_identity_file(self, ssh_config_dir):
        """Test getting host config with identity file."""
        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = ssh_config_dir.parent
            config = SSHConfig()

            host_config = config.get_host_config("testhost")

            assert host_config["identityfile"] is not None

    def test_get_profile_found(self, opszen_config_dir):
        """Test getting existing profile."""
        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = opszen_config_dir.parent
            config = SSHConfig()

            profile = config.get_profile("myserver")

            assert profile is not None
            assert profile["hostname"] == "192.168.1.50"
            assert profile["username"] == "admin"

    def test_get_profile_not_found(self):
        """Test getting non-existent profile."""
        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = Path("/home/test")
            config = SSHConfig()

            profile = config.get_profile("nonexistent")
            assert profile is None

    def test_save_profile_new(self, temp_dir):
        """Test saving a new connection profile."""
        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = temp_dir
            config = SSHConfig()

            config.save_profile(
                name="newserver",
                hostname="example.com",
                username="admin",
                port=22,
                key_file="/path/to/key",
            )

            assert "newserver" in config.profiles
            assert config.profiles["newserver"]["hostname"] == "example.com"
            assert config.profiles["newserver"]["username"] == "admin"

    def test_save_profile_update_existing(self, opszen_config_dir):
        """Test updating an existing profile."""
        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = opszen_config_dir.parent
            config = SSHConfig()

            config.save_profile(
                name="myserver",
                hostname="new.example.com",
                username="newuser",
                port=2222,
            )

            assert config.profiles["myserver"]["hostname"] == "new.example.com"
            assert config.profiles["myserver"]["username"] == "newuser"
            assert config.profiles["myserver"]["port"] == "2222"

    def test_save_profile_without_key(self, temp_dir):
        """Test saving profile without key file."""
        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = temp_dir
            config = SSHConfig()

            config.save_profile(name="nokey", hostname="example.com", username="user")

            assert "nokey" in config.profiles

    def test_save_profile_creates_directory(self, temp_dir):
        """Test that save_profile creates .opszen directory if missing."""
        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = temp_dir
            config = SSHConfig()

            config.save_profile(name="test", hostname="example.com", username="user")

            opszen_dir = temp_dir / ".opszen"
            assert opszen_dir.exists()

    def test_list_profiles_with_profiles(self, opszen_config_dir):
        """Test listing profiles when profiles exist."""
        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = opszen_config_dir.parent
            config = SSHConfig()

            # Should not raise exception
            config.list_profiles()

    def test_list_profiles_empty(self):
        """Test listing profiles when none exist."""
        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = Path("/home/test")
            config = SSHConfig()

            # Should handle empty profiles gracefully
            config.list_profiles()

    def test_delete_profile_success(self, opszen_config_dir):
        """Test deleting an existing profile."""
        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = opszen_config_dir.parent
            config = SSHConfig()

            config.delete_profile("myserver")

            assert "myserver" not in config.profiles

    def test_delete_profile_not_found(self):
        """Test deleting non-existent profile."""
        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = Path("/home/test")
            config = SSHConfig()

            # Should handle gracefully
            config.delete_profile("nonexistent")

    def test_find_key_files_found(self, ssh_config_dir):
        """Test finding SSH key files."""
        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = ssh_config_dir.parent
            config = SSHConfig()

            keys = config.find_key_files()

            assert len(keys) > 0
            assert any("id_rsa" in key for key in keys)

    def test_find_key_files_no_ssh_dir(self):
        """Test finding key files when .ssh directory doesn't exist."""
        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = Path("/home/test")
            config = SSHConfig()

            keys = config.find_key_files()
            assert keys == []

    def test_find_key_files_multiple_types(self, ssh_config_dir):
        """Test finding multiple types of SSH keys."""
        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = ssh_config_dir.parent
            config = SSHConfig()

            keys = config.find_key_files()

            # Should find both id_rsa and id_ed25519
            assert len(keys) >= 2

    def test_get_default_key_prefers_ed25519(self, ssh_config_dir):
        """Test that get_default_key prefers ed25519 over rsa."""
        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = ssh_config_dir.parent
            config = SSHConfig()

            default_key = config.get_default_key()

            assert default_key is not None
            assert "ed25519" in default_key

    def test_get_default_key_fallback_to_rsa(self, temp_dir):
        """Test that get_default_key falls back to rsa."""
        ssh_dir = temp_dir / ".ssh"
        ssh_dir.mkdir()
        (ssh_dir / "id_rsa").write_text("mock rsa key")

        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = temp_dir
            config = SSHConfig()

            default_key = config.get_default_key()

            assert default_key is not None
            assert "id_rsa" in default_key

    def test_get_default_key_no_keys(self):
        """Test get_default_key when no keys exist."""
        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = Path("/home/test")
            config = SSHConfig()

            default_key = config.get_default_key()
            assert default_key is None

    def test_save_profile_file_format(self, temp_dir):
        """Test that saved profile file is in correct format."""
        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = temp_dir
            config = SSHConfig()

            config.save_profile(
                name="test",
                hostname="test.com",
                username="testuser",
                port=22,
                key_file="/path/to/key",
            )

            profiles_file = temp_dir / ".opszen" / "ssh_profiles.conf"
            assert profiles_file.exists()

            # Verify file can be read as ConfigParser
            parser = configparser.ConfigParser()
            parser.read(profiles_file)
            assert "test" in parser.sections()

    def test_host_config_with_custom_port(self, temp_dir):
        """Test host config with custom port."""
        ssh_dir = temp_dir / ".ssh"
        ssh_dir.mkdir()
        config_file = ssh_dir / "config"
        config_content = """Host customport
    HostName example.com
    Port 2222
    User admin
"""
        config_file.write_text(config_content)

        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = temp_dir
            config = SSHConfig()

            host_config = config.get_host_config("customport")
            assert host_config["port"] == 2222

    def test_profiles_persistence(self, temp_dir):
        """Test that profiles persist across SSHConfig instances."""
        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = temp_dir

            # Create first instance and save profile
            config1 = SSHConfig()
            config1.save_profile(
                name="persistent", hostname="example.com", username="user"
            )

            # Create second instance and verify profile exists
            config2 = SSHConfig()
            profile = config2.get_profile("persistent")

            assert profile is not None
            assert profile["hostname"] == "example.com"

    def test_multiple_profiles(self, temp_dir):
        """Test managing multiple profiles."""
        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = temp_dir
            config = SSHConfig()

            # Save multiple profiles
            for i in range(5):
                config.save_profile(
                    name=f"server{i}",
                    hostname=f"server{i}.example.com",
                    username="admin",
                )

            assert len(config.profiles) == 5
            for i in range(5):
                assert f"server{i}" in config.profiles
