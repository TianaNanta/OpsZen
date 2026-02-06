#!/usr/bin/env python3
"""
Configuration Manager for OpsZen

Provides centralized configuration management with hierarchical settings:
1. Built-in defaults
2. config.yaml file
3. Environment variables
4. Runtime overrides

Supports:
- AWS profile management
- SSH configuration
- Docker daemon settings
- Application preferences
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from dotenv import load_dotenv
from rich.console import Console


class ConfigManager:
    """Centralized configuration management for OpsZen."""

    # Default configuration values
    DEFAULTS = {
        "aws": {
            "default_profile": "default",
            "default_region": "us-west-2",
            "default_instance_type": "t2.micro",
            "default_ami": "ami-0c55b159cbfafe1f0",  # Amazon Linux 2
            "timeout": 300,
            "max_retries": 3,
        },
        "ssh": {
            "default_user": "ec2-user",
            "default_port": 22,
            "connect_timeout": 10,
            "banner_timeout": 30,
            "auth_timeout": 30,
            "key_directory": "~/.ssh",
            "config_file": "~/.ssh/config",
            "use_ssh_config": True,
            "auto_add_host": False,
        },
        "docker": {
            "daemon_url": "unix:///var/run/docker.sock",
            "timeout": 60,
            "tls_verify": False,
            "default_network": "bridge",
            "auto_remove": False,
            "pull_policy": "missing",  # always, missing, never
        },
        "logging": {
            "level": "INFO",
            "format": "generic",  # generic, json, syslog, apache, python
            "output_dir": "~/.opszen/logs",
            "max_file_size": "10MB",
            "backup_count": 5,
            "console_output": True,
        },
        "application": {
            "config_dir": "~/.opszen",
            "data_dir": "~/.opszen/data",
            "cache_dir": "~/.opszen/cache",
            "profiles_file": "~/.opszen/profiles.yaml",
            "history_file": "~/.opszen/history.log",
            "theme": "auto",  # auto, light, dark
            "color_output": True,
            "verbose": False,
        },
        "monitoring": {
            "refresh_interval": 5,
            "history_size": 100,
            "alert_thresholds": {
                "cpu": 80,
                "memory": 85,
                "disk": 90,
            },
        },
    }

    def __init__(
        self,
        config_file: Optional[str] = None,
        load_env: bool = True,
        create_dirs: bool = True,
    ):
        """
        Initialize the configuration manager.

        Args:
            config_file: Path to config.yaml (default: ~/.opszen/config.yaml)
            load_env: Whether to load .env file
            create_dirs: Whether to create config directories if they don't exist
        """
        self.console = Console()
        self._config: Dict[str, Any] = {}
        self._profiles: Dict[str, Dict[str, Any]] = {}

        # Load environment variables from .env
        if load_env:
            self._load_env_file()

        # Determine config file path
        if config_file is None:
            config_file = os.getenv(
                "OPSZEN_CONFIG", str(Path.home() / ".opszen" / "config.yaml")
            )

        self.config_file = Path(config_file).expanduser()

        # Initialize configuration
        self._load_config()

        # Create necessary directories
        if create_dirs:
            self._create_directories()

    def _load_env_file(self):
        """Load environment variables from .env file."""
        env_file = Path.cwd() / ".env"
        if env_file.exists():
            load_dotenv(env_file)
            self.console.print(
                f"[dim]Loaded environment from {env_file}[/dim]", style="dim"
            )

    def _load_config(self):
        """Load configuration with hierarchical precedence."""
        # Start with defaults
        self._config = self._deep_copy(self.DEFAULTS)

        # Override with config.yaml if it exists
        if self.config_file.exists():
            try:
                with open(self.config_file) as f:
                    yaml_config = yaml.safe_load(f) or {}
                    self._merge_config(self._config, yaml_config)
                self.console.print(
                    f"[dim]Loaded configuration from {self.config_file}[/dim]",
                    style="dim",
                )
            except Exception as e:
                self.console.print(
                    f"[yellow]Warning: Could not load config file: {e}[/yellow]"
                )

        # Override with environment variables
        self._apply_env_overrides()

        # Expand paths
        self._expand_paths()

    def _deep_copy(self, obj: Any) -> Any:
        """Create a deep copy of the object."""
        if isinstance(obj, dict):
            return {k: self._deep_copy(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._deep_copy(item) for item in obj]
        else:
            return obj

    def _merge_config(self, base: Dict, override: Dict):
        """Recursively merge override config into base config."""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value

    def _apply_env_overrides(self):
        """Apply environment variable overrides."""
        # AWS configuration
        if os.getenv("AWS_PROFILE"):
            self._config["aws"]["default_profile"] = os.getenv("AWS_PROFILE")
        if os.getenv("AWS_REGION"):
            self._config["aws"]["default_region"] = os.getenv("AWS_REGION")
        if os.getenv("AWS_DEFAULT_REGION"):
            self._config["aws"]["default_region"] = os.getenv("AWS_DEFAULT_REGION")

        # SSH configuration
        if os.getenv("OPSZEN_SSH_USER"):
            self._config["ssh"]["default_user"] = os.getenv("OPSZEN_SSH_USER")
        if os.getenv("OPSZEN_SSH_KEY"):
            self._config["ssh"]["default_key"] = os.getenv("OPSZEN_SSH_KEY")

        # Docker configuration
        if os.getenv("DOCKER_HOST"):
            self._config["docker"]["daemon_url"] = os.getenv("DOCKER_HOST")
        if os.getenv("DOCKER_TLS_VERIFY"):
            self._config["docker"]["tls_verify"] = os.getenv("DOCKER_TLS_VERIFY") == "1"
        if os.getenv("DOCKER_CERT_PATH"):
            self._config["docker"]["cert_path"] = os.getenv("DOCKER_CERT_PATH")

        # Logging configuration
        if os.getenv("OPSZEN_LOG_LEVEL"):
            self._config["logging"]["level"] = os.getenv("OPSZEN_LOG_LEVEL")
        if os.getenv("OPSZEN_VERBOSE"):
            self._config["application"]["verbose"] = os.getenv(
                "OPSZEN_VERBOSE"
            ).lower() in ("1", "true", "yes")

    def _expand_paths(self):
        """Expand ~ and environment variables in path configurations."""
        path_keys = {
            "ssh": ["key_directory", "config_file"],
            "logging": ["output_dir"],
            "application": [
                "config_dir",
                "data_dir",
                "cache_dir",
                "profiles_file",
                "history_file",
            ],
        }

        for section, keys in path_keys.items():
            if section in self._config:
                for key in keys:
                    if key in self._config[section]:
                        value = self._config[section][key]
                        if isinstance(value, str):
                            self._config[section][key] = str(
                                Path(value).expanduser().absolute()
                            )

    def _create_directories(self):
        """Create necessary configuration directories."""
        dirs_to_create = [
            self._config["application"]["config_dir"],
            self._config["application"]["data_dir"],
            self._config["application"]["cache_dir"],
            self._config["logging"]["output_dir"],
        ]

        for dir_path in dirs_to_create:
            path = Path(dir_path)
            if not path.exists():
                try:
                    path.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    self.console.print(
                        f"[yellow]Warning: Could not create directory {path}: {e}[/yellow]"
                    )

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation.

        Args:
            key: Configuration key in dot notation (e.g., "aws.default_region")
            default: Default value if key doesn't exist

        Returns:
            Configuration value or default

        Example:
            >>> config.get("aws.default_region")
            "us-west-2"
        """
        keys = key.split(".")
        value = self._config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any):
        """
        Set a configuration value using dot notation.

        Args:
            key: Configuration key in dot notation
            value: Value to set

        Example:
            >>> config.set("aws.default_region", "us-east-1")
        """
        keys = key.split(".")
        target = self._config

        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            target = target[k]

        target[keys[-1]] = value

    def get_section(self, section: str) -> Dict[str, Any]:
        """
        Get an entire configuration section.

        Args:
            section: Section name (e.g., "aws", "ssh", "docker")

        Returns:
            Configuration section as dictionary
        """
        return self._config.get(section, {})

    def get_aws_profile(self, profile_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get AWS profile configuration.

        Args:
            profile_name: Profile name (uses default if None)

        Returns:
            AWS profile configuration
        """
        if profile_name is None:
            profile_name = self.get("aws.default_profile", "default")

        # Check for profile-specific configuration
        profiles = self.get("aws.profiles", {})
        if profile_name in profiles:
            profile = self._deep_copy(self.get_section("aws"))
            profile.update(profiles[profile_name])
            return profile

        return self.get_section("aws")

    def list_aws_profiles(self) -> List[str]:
        """
        List all configured AWS profiles.

        Returns:
            List of profile names
        """
        profiles = self.get("aws.profiles", {})
        return list(profiles.keys())

    def get_ssh_config(self, host: Optional[str] = None) -> Dict[str, Any]:
        """
        Get SSH configuration, optionally for a specific host.

        Args:
            host: Host to get configuration for

        Returns:
            SSH configuration dictionary
        """
        config = self.get_section("ssh")

        # If host-specific config exists, merge it
        if host and "hosts" in config and host in config["hosts"]:
            host_config = self._deep_copy(config)
            host_config.update(config["hosts"][host])
            return host_config

        return config

    def get_docker_config(self) -> Dict[str, Any]:
        """
        Get Docker configuration.

        Returns:
            Docker configuration dictionary
        """
        return self.get_section("docker")

    def save_config(self, backup: bool = True):
        """
        Save current configuration to config.yaml.

        Args:
            backup: Whether to create a backup of existing config
        """
        # Create config directory if it doesn't exist
        self.config_file.parent.mkdir(parents=True, exist_ok=True)

        # Backup existing config
        if backup and self.config_file.exists():
            backup_file = self.config_file.with_suffix(".yaml.backup")
            self.config_file.rename(backup_file)
            self.console.print(f"[dim]Backed up config to {backup_file}[/dim]")

        # Save configuration
        try:
            with open(self.config_file, "w") as f:
                yaml.dump(self._config, f, default_flow_style=False, sort_keys=False)
            self.console.print(
                f"[green]Configuration saved to {self.config_file}[/green]"
            )
        except Exception as e:
            self.console.print(f"[red]Error saving configuration: {e}[/red]")
            raise

    def reload(self):
        """Reload configuration from file and environment."""
        self._load_config()
        self.console.print("[green]Configuration reloaded[/green]")

    def validate(self) -> bool:
        """
        Validate the current configuration.

        Returns:
            True if configuration is valid, False otherwise
        """
        errors = []

        # Validate AWS configuration
        aws_config = self.get_section("aws")
        if not aws_config.get("default_region"):
            errors.append("AWS default_region is not set")

        # Validate SSH configuration
        ssh_config = self.get_section("ssh")
        if ssh_config.get("connect_timeout", 0) <= 0:
            errors.append("SSH connect_timeout must be positive")

        # Validate Docker configuration
        docker_config = self.get_section("docker")
        if not docker_config.get("daemon_url"):
            errors.append("Docker daemon_url is not set")

        # Print errors
        if errors:
            self.console.print("[red]Configuration validation errors:[/red]")
            for error in errors:
                self.console.print(f"  - {error}")
            return False

        self.console.print("[green]Configuration is valid[/green]")
        return True

    def print_config(self, section: Optional[str] = None):
        """
        Print configuration to console.

        Args:
            section: Specific section to print (prints all if None)
        """
        from rich.tree import Tree

        tree = Tree("🔧 OpsZen Configuration", guide_style="dim")

        config_to_print = (
            self._config if section is None else {section: self.get_section(section)}
        )

        for key, value in config_to_print.items():
            self._add_to_tree(tree, key, value)

        self.console.print(tree)

    def _add_to_tree(self, parent, key: str, value: Any):
        """Recursively add configuration to tree."""
        if isinstance(value, dict):
            branch = parent.add(f"[bold cyan]{key}[/bold cyan]")
            for k, v in value.items():
                self._add_to_tree(branch, k, v)
        elif isinstance(value, list):
            branch = parent.add(f"[bold cyan]{key}[/bold cyan]")
            for item in value:
                branch.add(f"• {item}")
        else:
            parent.add(f"[cyan]{key}[/cyan]: [yellow]{value}[/yellow]")

    def __repr__(self) -> str:
        return f"ConfigManager(config_file='{self.config_file}')"
