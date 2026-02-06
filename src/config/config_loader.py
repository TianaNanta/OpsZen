#!/usr/bin/env python3
"""
Configuration Loader for OpsZen

Provides utilities for loading and parsing configuration files
from various sources and formats.
"""

import contextlib
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional, Union

import yaml
from rich.console import Console


class ConfigLoader:
    """Utility class for loading configuration from various sources."""

    def __init__(self):
        """Initialize the configuration loader."""
        self.console = Console()

    @staticmethod
    def load_yaml(file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Load configuration from a YAML file.

        Args:
            file_path: Path to YAML file

        Returns:
            Parsed configuration dictionary

        Raises:
            FileNotFoundError: If file doesn't exist
            yaml.YAMLError: If file is not valid YAML
        """
        path = Path(file_path).expanduser()

        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")

        with open(path) as f:
            return yaml.safe_load(f) or {}

    @staticmethod
    def load_json(file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Load configuration from a JSON file.

        Args:
            file_path: Path to JSON file

        Returns:
            Parsed configuration dictionary

        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If file is not valid JSON
        """
        path = Path(file_path).expanduser()

        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")

        with open(path) as f:
            return json.load(f)

    @staticmethod
    def save_yaml(data: Dict[str, Any], file_path: Union[str, Path]):
        """
        Save configuration to a YAML file.

        Args:
            data: Configuration data to save
            file_path: Path to output YAML file
        """
        path = Path(file_path).expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)

    @staticmethod
    def save_json(data: Dict[str, Any], file_path: Union[str, Path], indent: int = 2):
        """
        Save configuration to a JSON file.

        Args:
            data: Configuration data to save
            file_path: Path to output JSON file
            indent: JSON indentation level
        """
        path = Path(file_path).expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w") as f:
            json.dump(data, f, indent=indent)

    @staticmethod
    def load_env_file(file_path: Union[str, Path]) -> Dict[str, str]:
        """
        Load environment variables from a .env file.

        Args:
            file_path: Path to .env file

        Returns:
            Dictionary of environment variables
        """
        path = Path(file_path).expanduser()
        env_vars = {}

        if not path.exists():
            return env_vars

        with open(path) as f:
            for line in f:
                line = line.strip()

                # Skip comments and empty lines
                if not line or line.startswith("#"):
                    continue

                # Parse KEY=VALUE format
                if "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip()

                    # Remove quotes if present
                    if (
                        value.startswith('"')
                        and value.endswith('"')
                        or value.startswith("'")
                        and value.endswith("'")
                    ):
                        value = value[1:-1]

                    env_vars[key] = value

        return env_vars

    def discover_config_file(
        self, config_name: str = "config.yaml", search_paths: Optional[list] = None
    ) -> Optional[Path]:
        """
        Discover configuration file by searching common locations.

        Args:
            config_name: Name of config file to search for
            search_paths: Custom list of paths to search (optional)

        Returns:
            Path to found config file, or None if not found

        Search order:
            1. Current directory
            2. ~/.opszen/
            3. /etc/opszen/
            4. Custom search paths (if provided)
        """
        if search_paths is None:
            search_paths = [
                Path.cwd(),
                Path.home() / ".opszen",
                Path("/etc/opszen"),
            ]

        for search_path in search_paths:
            config_path = Path(search_path) / config_name
            if config_path.exists():
                self.console.print(
                    f"[dim]Found config at {config_path}[/dim]", style="dim"
                )
                return config_path

        return None

    def merge_configs(
        self, *configs: Dict[str, Any], deep: bool = True
    ) -> Dict[str, Any]:
        """
        Merge multiple configuration dictionaries.

        Args:
            *configs: Configuration dictionaries to merge
            deep: Whether to perform deep merge (nested dicts)

        Returns:
            Merged configuration dictionary

        Note:
            Later configs override earlier ones.
        """
        result = {}

        for config in configs:
            if not config:
                continue

            if deep:
                self._deep_merge(result, config)
            else:
                result.update(config)

        return result

    def _deep_merge(self, base: Dict, override: Dict):
        """
        Recursively merge override dict into base dict.

        Args:
            base: Base dictionary (modified in place)
            override: Override dictionary
        """
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value

    def validate_schema(self, config: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        """
        Validate configuration against a simple schema.

        Args:
            config: Configuration to validate
            schema: Schema definition

        Returns:
            True if valid, False otherwise

        Schema format:
            {
                "required_keys": ["key1", "key2"],
                "optional_keys": ["key3"],
                "nested": {
                    "key1": {
                        "required_keys": ["subkey1"]
                    }
                }
            }
        """
        errors = []

        # Check required keys
        required_keys = schema.get("required_keys", [])
        for key in required_keys:
            if key not in config:
                errors.append(f"Missing required key: {key}")

        # Validate nested schemas
        nested_schemas = schema.get("nested", {})
        for key, nested_schema in nested_schemas.items():
            if (
                key in config
                and isinstance(config[key], dict)
                and not self.validate_schema(config[key], nested_schema)
            ):
                errors.append(f"Invalid nested config: {key}")

        if errors:
            self.console.print("[red]Configuration validation errors:[/red]")
            for error in errors:
                self.console.print(f"  - {error}")
            return False

        return True

    def create_example_config(
        self, output_path: Union[str, Path], template: Dict[str, Any]
    ):
        """
        Create an example configuration file with comments.

        Args:
            output_path: Path where example config should be created
            template: Template configuration with structure and defaults
        """
        path = Path(output_path).expanduser()

        # Don't overwrite existing config
        if path.exists():
            self.console.print(f"[yellow]Config file already exists: {path}[/yellow]")
            return

        # Create parent directory if needed
        path.parent.mkdir(parents=True, exist_ok=True)

        # Save template
        self.save_yaml(template, path)
        self.console.print(f"[green]Created example config at {path}[/green]")

    def get_config_from_env(self, prefix: str = "OPSZEN_") -> Dict[str, str]:
        """
        Extract configuration from environment variables with a given prefix.

        Args:
            prefix: Environment variable prefix to match

        Returns:
            Dictionary of config values from environment

        Example:
            OPSZEN_AWS_REGION=us-east-1 -> {"AWS_REGION": "us-east-1"}
        """
        config = {}

        for key, value in os.environ.items():
            if key.startswith(prefix):
                # Remove prefix
                config_key = key[len(prefix) :]
                config[config_key] = value

        return config

    def parse_config_string(self, config_str: str) -> Dict[str, Any]:
        """
        Parse configuration from a string in KEY=VALUE format.

        Args:
            config_str: Configuration string (e.g., "key1=value1,key2=value2")

        Returns:
            Parsed configuration dictionary
        """
        config = {}

        if not config_str:
            return config

        # Split by comma (handle quoted values)
        pairs = config_str.split(",")

        for pair in pairs:
            pair = pair.strip()
            if "=" in pair:
                key, value = pair.split("=", 1)
                key = key.strip()
                value = value.strip()

                # Try to parse as JSON for complex types
                with contextlib.suppress(json.JSONDecodeError, ValueError):
                    value = json.loads(value)

                config[key] = value

        return config

    def __repr__(self) -> str:
        return "ConfigLoader()"
