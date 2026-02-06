#!/usr/bin/env python3
"""
Unit tests for ConfigManager class.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from src.config.config_manager import ConfigManager


class TestConfigManager:
    """Test suite for ConfigManager class."""

    @pytest.fixture
    def temp_config_dir(self):
        """Create a temporary configuration directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def temp_config_file(self, temp_config_dir):
        """Create a temporary config file."""
        config_file = temp_config_dir / "config.yaml"
        config_data = {
            "aws": {
                "default_region": "us-east-1",
                "default_profile": "test",
            },
            "ssh": {
                "default_user": "ubuntu",
                "connect_timeout": 20,
            },
        }
        with open(config_file, "w") as f:
            yaml.dump(config_data, f)
        return config_file

    @pytest.fixture
    def config_manager(self, temp_config_file):
        """Create a ConfigManager instance with temp config."""
        return ConfigManager(
            config_file=str(temp_config_file), load_env=False, create_dirs=False
        )

    def test_initialization(self, config_manager):
        """Test ConfigManager initialization."""
        assert config_manager is not None
        assert config_manager._config is not None
        assert isinstance(config_manager._config, dict)

    def test_defaults_loaded(self):
        """Test that default configuration is loaded."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "nonexistent.yaml"
            manager = ConfigManager(
                config_file=str(config_file), load_env=False, create_dirs=False
            )

            # Check some default values
            assert manager.get("aws.default_region") == "us-west-2"
            assert manager.get("ssh.default_port") == 22
            assert manager.get("docker.timeout") == 60

    def test_config_file_overrides_defaults(self, config_manager):
        """Test that config file values override defaults."""
        # These should be from the config file
        assert config_manager.get("aws.default_region") == "us-east-1"
        assert config_manager.get("aws.default_profile") == "test"
        assert config_manager.get("ssh.default_user") == "ubuntu"
        assert config_manager.get("ssh.connect_timeout") == 20

        # These should still be defaults (not in config file)
        assert config_manager.get("ssh.default_port") == 22
        assert config_manager.get("docker.timeout") == 60

    def test_get_with_dot_notation(self, config_manager):
        """Test getting values with dot notation."""
        assert config_manager.get("aws.default_region") == "us-east-1"
        assert config_manager.get("ssh.connect_timeout") == 20

    def test_get_with_default(self, config_manager):
        """Test getting values with default fallback."""
        assert config_manager.get("nonexistent.key", "default_value") == "default_value"
        assert config_manager.get("aws.nonexistent", 42) == 42

    def test_get_nested_value(self, config_manager):
        """Test getting deeply nested values."""
        config_manager.set("level1.level2.level3", "deep_value")
        assert config_manager.get("level1.level2.level3") == "deep_value"

    def test_set_value(self, config_manager):
        """Test setting configuration values."""
        config_manager.set("aws.default_region", "eu-west-1")
        assert config_manager.get("aws.default_region") == "eu-west-1"

    def test_set_nested_value(self, config_manager):
        """Test setting deeply nested values."""
        config_manager.set("new.nested.key", "value")
        assert config_manager.get("new.nested.key") == "value"

    def test_get_section(self, config_manager):
        """Test getting entire configuration section."""
        aws_config = config_manager.get_section("aws")
        assert isinstance(aws_config, dict)
        assert "default_region" in aws_config
        assert "default_profile" in aws_config

    def test_get_section_nonexistent(self, config_manager):
        """Test getting nonexistent section returns empty dict."""
        section = config_manager.get_section("nonexistent")
        assert section == {}

    def test_get_aws_profile_default(self, config_manager):
        """Test getting default AWS profile."""
        profile = config_manager.get_aws_profile()
        assert isinstance(profile, dict)
        assert "default_region" in profile

    def test_get_aws_profile_specific(self, temp_config_file):
        """Test getting specific AWS profile."""
        # Add profiles to config
        config_data = {
            "aws": {
                "default_profile": "default",
                "profiles": {
                    "prod": {"region": "us-east-1", "instance_type": "t3.large"},
                    "dev": {"region": "us-west-2", "instance_type": "t2.micro"},
                },
            }
        }
        with open(temp_config_file, "w") as f:
            yaml.dump(config_data, f)

        manager = ConfigManager(
            config_file=str(temp_config_file), load_env=False, create_dirs=False
        )

        prod_profile = manager.get_aws_profile("prod")
        assert prod_profile["region"] == "us-east-1"
        assert prod_profile["instance_type"] == "t3.large"

    def test_list_aws_profiles(self, temp_config_file):
        """Test listing AWS profiles."""
        config_data = {
            "aws": {
                "profiles": {
                    "prod": {"region": "us-east-1"},
                    "dev": {"region": "us-west-2"},
                    "staging": {"region": "eu-west-1"},
                }
            }
        }
        with open(temp_config_file, "w") as f:
            yaml.dump(config_data, f)

        manager = ConfigManager(
            config_file=str(temp_config_file), load_env=False, create_dirs=False
        )

        profiles = manager.list_aws_profiles()
        assert "prod" in profiles
        assert "dev" in profiles
        assert "staging" in profiles
        assert len(profiles) == 3

    def test_list_aws_profiles_empty(self, config_manager):
        """Test listing AWS profiles when none are configured."""
        profiles = config_manager.list_aws_profiles()
        assert profiles == []

    def test_get_ssh_config_default(self, config_manager):
        """Test getting default SSH configuration."""
        ssh_config = config_manager.get_ssh_config()
        assert isinstance(ssh_config, dict)
        assert "default_user" in ssh_config
        assert ssh_config["default_user"] == "ubuntu"

    def test_get_ssh_config_host_specific(self, temp_config_file):
        """Test getting host-specific SSH configuration."""
        config_data = {
            "ssh": {
                "default_user": "ec2-user",
                "hosts": {
                    "web-server": {"user": "ubuntu", "port": 2222},
                    "db-server": {"user": "postgres", "port": 22},
                },
            }
        }
        with open(temp_config_file, "w") as f:
            yaml.dump(config_data, f)

        manager = ConfigManager(
            config_file=str(temp_config_file), load_env=False, create_dirs=False
        )

        web_config = manager.get_ssh_config("web-server")
        assert web_config["user"] == "ubuntu"
        assert web_config["port"] == 2222

    def test_get_docker_config(self, config_manager):
        """Test getting Docker configuration."""
        docker_config = config_manager.get_docker_config()
        assert isinstance(docker_config, dict)
        assert "daemon_url" in docker_config
        assert "timeout" in docker_config

    def test_save_config(self, temp_config_dir):
        """Test saving configuration to file."""
        config_file = temp_config_dir / "new_config.yaml"
        manager = ConfigManager(
            config_file=str(config_file), load_env=False, create_dirs=False
        )

        manager.set("test.key", "test_value")
        manager.save_config(backup=False)

        # Verify file was created
        assert config_file.exists()

        # Verify content
        with open(config_file) as f:
            saved_config = yaml.safe_load(f)
        assert saved_config["test"]["key"] == "test_value"

    def test_save_config_with_backup(self, temp_config_file):
        """Test saving configuration with backup."""
        manager = ConfigManager(
            config_file=str(temp_config_file), load_env=False, create_dirs=False
        )

        manager.set("test.key", "new_value")
        manager.save_config(backup=True)

        # Check backup was created
        backup_file = temp_config_file.with_suffix(".yaml.backup")
        assert backup_file.exists()

    def test_reload_config(self, temp_config_file):
        """Test reloading configuration from file."""
        manager = ConfigManager(
            config_file=str(temp_config_file), load_env=False, create_dirs=False
        )

        # Modify config in memory
        manager.set("aws.default_region", "ap-south-1")
        assert manager.get("aws.default_region") == "ap-south-1"

        # Reload should reset to file values
        manager.reload()
        assert manager.get("aws.default_region") == "us-east-1"

    def test_validate_valid_config(self, config_manager):
        """Test validation of valid configuration."""
        assert config_manager.validate() is True

    def test_validate_invalid_config(self, temp_config_file):
        """Test validation of invalid configuration."""
        # Create config with missing required fields
        config_data = {
            "aws": {
                "default_region": "",  # Empty region
            },
            "ssh": {
                "connect_timeout": -5,  # Negative timeout
            },
            "docker": {
                "daemon_url": "",  # Empty daemon URL
            },
        }
        with open(temp_config_file, "w") as f:
            yaml.dump(config_data, f)

        manager = ConfigManager(
            config_file=str(temp_config_file), load_env=False, create_dirs=False
        )

        assert manager.validate() is False

    @patch.dict(os.environ, {"AWS_PROFILE": "custom-profile"})
    def test_env_override_aws_profile(self, temp_config_file):
        """Test that AWS_PROFILE environment variable overrides config."""
        manager = ConfigManager(
            config_file=str(temp_config_file), load_env=True, create_dirs=False
        )
        assert manager.get("aws.default_profile") == "custom-profile"

    @patch.dict(os.environ, {"AWS_REGION": "ap-northeast-1"})
    def test_env_override_aws_region(self, temp_config_file):
        """Test that AWS_REGION environment variable overrides config."""
        manager = ConfigManager(
            config_file=str(temp_config_file), load_env=True, create_dirs=False
        )
        assert manager.get("aws.default_region") == "ap-northeast-1"

    @patch.dict(os.environ, {"DOCKER_HOST": "tcp://192.168.1.100:2375"})
    def test_env_override_docker_host(self, temp_config_file):
        """Test that DOCKER_HOST environment variable overrides config."""
        manager = ConfigManager(
            config_file=str(temp_config_file), load_env=True, create_dirs=False
        )
        assert manager.get("docker.daemon_url") == "tcp://192.168.1.100:2375"

    @patch.dict(os.environ, {"OPSZEN_SSH_USER": "admin"})
    def test_env_override_ssh_user(self, temp_config_file):
        """Test that OPSZEN_SSH_USER environment variable overrides config."""
        manager = ConfigManager(
            config_file=str(temp_config_file), load_env=True, create_dirs=False
        )
        assert manager.get("ssh.default_user") == "admin"

    @patch.dict(os.environ, {"OPSZEN_VERBOSE": "true"})
    def test_env_override_verbose(self, temp_config_file):
        """Test that OPSZEN_VERBOSE environment variable overrides config."""
        manager = ConfigManager(
            config_file=str(temp_config_file), load_env=True, create_dirs=False
        )
        assert manager.get("application.verbose") is True

    def test_path_expansion(self, config_manager):
        """Test that paths with ~ are expanded."""
        ssh_key_dir = config_manager.get("ssh.key_directory")
        assert "~" not in ssh_key_dir
        assert ssh_key_dir.startswith("/")

    def test_deep_merge_preserves_unrelated_keys(self, temp_config_file):
        """Test that merging configs preserves unrelated keys."""
        config_data = {
            "aws": {"default_region": "us-east-1", "timeout": 600},
            "ssh": {"default_user": "ubuntu"},
        }
        with open(temp_config_file, "w") as f:
            yaml.dump(config_data, f)

        manager = ConfigManager(
            config_file=str(temp_config_file), load_env=False, create_dirs=False
        )

        # Both file values and defaults should be present
        assert manager.get("aws.default_region") == "us-east-1"  # From file
        assert manager.get("aws.timeout") == 600  # From file
        assert manager.get("aws.max_retries") == 3  # From defaults
        assert manager.get("ssh.default_user") == "ubuntu"  # From file
        assert manager.get("ssh.default_port") == 22  # From defaults

    def test_config_file_not_found(self, temp_config_dir):
        """Test handling of missing config file."""
        nonexistent_file = temp_config_dir / "does_not_exist.yaml"
        manager = ConfigManager(
            config_file=str(nonexistent_file), load_env=False, create_dirs=False
        )

        # Should fall back to defaults
        assert manager.get("aws.default_region") == "us-west-2"

    def test_malformed_config_file(self, temp_config_file):
        """Test handling of malformed YAML config file."""
        # Write invalid YAML
        with open(temp_config_file, "w") as f:
            f.write("invalid: yaml: content:\n  - broken")

        # Should not crash, fall back to defaults
        manager = ConfigManager(
            config_file=str(temp_config_file), load_env=False, create_dirs=False
        )

        assert manager.get("aws.default_region") == "us-west-2"

    def test_print_config(self, config_manager, capsys):
        """Test printing configuration."""
        config_manager.print_config()
        # Just verify it doesn't crash
        # Rich output is hard to test precisely

    def test_print_config_section(self, config_manager, capsys):
        """Test printing specific configuration section."""
        config_manager.print_config(section="aws")
        # Just verify it doesn't crash

    def test_repr(self, config_manager):
        """Test string representation."""
        repr_str = repr(config_manager)
        assert "ConfigManager" in repr_str
        assert "config_file" in repr_str
