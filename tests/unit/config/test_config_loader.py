#!/usr/bin/env python3
"""
Unit tests for ConfigLoader class.
"""

import json
import tempfile
from pathlib import Path

import pytest
import yaml

from src.config.config_loader import ConfigLoader


class TestConfigLoader:
    """Test suite for ConfigLoader class."""

    @pytest.fixture
    def loader(self):
        """Create a ConfigLoader instance."""
        return ConfigLoader()

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def sample_yaml_file(self, temp_dir):
        """Create a sample YAML file."""
        yaml_file = temp_dir / "test.yaml"
        data = {
            "key1": "value1",
            "key2": {"nested": "value2"},
            "key3": [1, 2, 3],
        }
        with open(yaml_file, "w") as f:
            yaml.dump(data, f)
        return yaml_file

    @pytest.fixture
    def sample_json_file(self, temp_dir):
        """Create a sample JSON file."""
        json_file = temp_dir / "test.json"
        data = {
            "key1": "value1",
            "key2": {"nested": "value2"},
            "key3": [1, 2, 3],
        }
        with open(json_file, "w") as f:
            json.dump(data, f)
        return json_file

    @pytest.fixture
    def sample_env_file(self, temp_dir):
        """Create a sample .env file."""
        env_file = temp_dir / ".env"
        content = """
# Comment line
KEY1=value1
KEY2="quoted value"
KEY3='single quoted'
EMPTY_KEY=

# Another comment
KEY4=value4
"""
        env_file.write_text(content)
        return env_file

    def test_initialization(self, loader):
        """Test ConfigLoader initialization."""
        assert loader is not None
        assert loader.console is not None

    def test_load_yaml_success(self, loader, sample_yaml_file):
        """Test loading YAML file successfully."""
        data = loader.load_yaml(sample_yaml_file)
        assert isinstance(data, dict)
        assert data["key1"] == "value1"
        assert data["key2"]["nested"] == "value2"
        assert data["key3"] == [1, 2, 3]

    def test_load_yaml_file_not_found(self, loader, temp_dir):
        """Test loading non-existent YAML file."""
        nonexistent = temp_dir / "nonexistent.yaml"
        with pytest.raises(FileNotFoundError):
            loader.load_yaml(nonexistent)

    def test_load_yaml_invalid_content(self, loader, temp_dir):
        """Test loading invalid YAML file."""
        invalid_yaml = temp_dir / "invalid.yaml"
        invalid_yaml.write_text("invalid: yaml: content:\n  - [broken")
        with pytest.raises(yaml.YAMLError):
            loader.load_yaml(invalid_yaml)

    def test_load_yaml_empty_file(self, loader, temp_dir):
        """Test loading empty YAML file."""
        empty_yaml = temp_dir / "empty.yaml"
        empty_yaml.write_text("")
        data = loader.load_yaml(empty_yaml)
        assert data == {}

    def test_load_json_success(self, loader, sample_json_file):
        """Test loading JSON file successfully."""
        data = loader.load_json(sample_json_file)
        assert isinstance(data, dict)
        assert data["key1"] == "value1"
        assert data["key2"]["nested"] == "value2"
        assert data["key3"] == [1, 2, 3]

    def test_load_json_file_not_found(self, loader, temp_dir):
        """Test loading non-existent JSON file."""
        nonexistent = temp_dir / "nonexistent.json"
        with pytest.raises(FileNotFoundError):
            loader.load_json(nonexistent)

    def test_load_json_invalid_content(self, loader, temp_dir):
        """Test loading invalid JSON file."""
        invalid_json = temp_dir / "invalid.json"
        invalid_json.write_text("{invalid json}")
        with pytest.raises(json.JSONDecodeError):
            loader.load_json(invalid_json)

    def test_save_yaml(self, loader, temp_dir):
        """Test saving data to YAML file."""
        output_file = temp_dir / "output.yaml"
        data = {"key1": "value1", "key2": {"nested": "value2"}}

        loader.save_yaml(data, output_file)

        assert output_file.exists()
        loaded_data = loader.load_yaml(output_file)
        assert loaded_data == data

    def test_save_yaml_creates_parent_dirs(self, loader, temp_dir):
        """Test that save_yaml creates parent directories."""
        output_file = temp_dir / "nested" / "dirs" / "output.yaml"
        data = {"test": "data"}

        loader.save_yaml(data, output_file)

        assert output_file.exists()
        assert output_file.parent.exists()

    def test_save_json(self, loader, temp_dir):
        """Test saving data to JSON file."""
        output_file = temp_dir / "output.json"
        data = {"key1": "value1", "key2": {"nested": "value2"}}

        loader.save_json(data, output_file)

        assert output_file.exists()
        loaded_data = loader.load_json(output_file)
        assert loaded_data == data

    def test_save_json_with_custom_indent(self, loader, temp_dir):
        """Test saving JSON with custom indentation."""
        output_file = temp_dir / "output.json"
        data = {"key": "value"}

        loader.save_json(data, output_file, indent=4)

        assert output_file.exists()
        content = output_file.read_text()
        assert "    " in content  # 4-space indent

    def test_load_env_file_success(self, loader, sample_env_file):
        """Test loading .env file successfully."""
        env_vars = loader.load_env_file(sample_env_file)

        assert isinstance(env_vars, dict)
        assert env_vars["KEY1"] == "value1"
        assert env_vars["KEY2"] == "quoted value"
        assert env_vars["KEY3"] == "single quoted"
        assert env_vars["KEY4"] == "value4"

    def test_load_env_file_empty_values(self, loader, sample_env_file):
        """Test loading .env file with empty values."""
        env_vars = loader.load_env_file(sample_env_file)
        assert env_vars["EMPTY_KEY"] == ""

    def test_load_env_file_not_found(self, loader, temp_dir):
        """Test loading non-existent .env file."""
        nonexistent = temp_dir / ".env"
        env_vars = loader.load_env_file(nonexistent)
        assert env_vars == {}

    def test_load_env_file_ignores_comments(self, loader, temp_dir):
        """Test that comments are ignored in .env files."""
        env_file = temp_dir / ".env"
        env_file.write_text("# This is a comment\nKEY=value\n# Another comment")

        env_vars = loader.load_env_file(env_file)
        assert len(env_vars) == 1
        assert env_vars["KEY"] == "value"

    def test_discover_config_file_in_current_dir(self, loader, temp_dir):
        """Test discovering config file in current directory."""
        config_file = temp_dir / "config.yaml"
        config_file.write_text("test: config")

        found = loader.discover_config_file(
            config_name="config.yaml", search_paths=[temp_dir]
        )

        assert found == config_file

    def test_discover_config_file_not_found(self, loader, temp_dir):
        """Test config file not found returns None."""
        found = loader.discover_config_file(
            config_name="nonexistent.yaml", search_paths=[temp_dir]
        )
        assert found is None

    def test_discover_config_file_search_order(self, loader, temp_dir):
        """Test that config discovery follows search order."""
        dir1 = temp_dir / "dir1"
        dir2 = temp_dir / "dir2"
        dir1.mkdir()
        dir2.mkdir()

        config1 = dir1 / "config.yaml"
        config2 = dir2 / "config.yaml"
        config1.write_text("config: 1")
        config2.write_text("config: 2")

        # Should find dir1 first
        found = loader.discover_config_file(
            config_name="config.yaml", search_paths=[dir1, dir2]
        )
        assert found == config1

    def test_merge_configs_shallow(self, loader):
        """Test shallow merging of configs."""
        config1 = {"key1": "value1", "key2": "value2"}
        config2 = {"key2": "new_value2", "key3": "value3"}

        merged = loader.merge_configs(config1, config2, deep=False)

        assert merged["key1"] == "value1"
        assert merged["key2"] == "new_value2"  # Overridden
        assert merged["key3"] == "value3"

    def test_merge_configs_deep(self, loader):
        """Test deep merging of configs."""
        config1 = {
            "level1": {"key1": "value1", "nested": {"key2": "value2"}},
            "other": "value",
        }
        config2 = {"level1": {"key1": "new_value1", "nested": {"key3": "value3"}}}

        merged = loader.merge_configs(config1, config2, deep=True)

        assert merged["level1"]["key1"] == "new_value1"  # Overridden
        assert merged["level1"]["nested"]["key2"] == "value2"  # Preserved
        assert merged["level1"]["nested"]["key3"] == "value3"  # Added
        assert merged["other"] == "value"  # Preserved

    def test_merge_configs_multiple(self, loader):
        """Test merging multiple configs."""
        config1 = {"key": "value1"}
        config2 = {"key": "value2"}
        config3 = {"key": "value3"}

        merged = loader.merge_configs(config1, config2, config3)

        assert merged["key"] == "value3"  # Last one wins

    def test_merge_configs_with_none(self, loader):
        """Test merging configs with None values."""
        config1 = {"key1": "value1"}
        config2 = None
        config3 = {"key2": "value2"}

        merged = loader.merge_configs(config1, config2, config3)

        assert merged["key1"] == "value1"
        assert merged["key2"] == "value2"

    def test_validate_schema_valid(self, loader):
        """Test validating a valid config against schema."""
        config = {"required_key": "value", "optional_key": "value"}
        schema = {"required_keys": ["required_key"], "optional_keys": ["optional_key"]}

        assert loader.validate_schema(config, schema) is True

    def test_validate_schema_missing_required_key(self, loader):
        """Test validation fails for missing required key."""
        config = {"optional_key": "value"}
        schema = {"required_keys": ["required_key"]}

        assert loader.validate_schema(config, schema) is False

    def test_validate_schema_nested(self, loader):
        """Test validating nested config."""
        config = {
            "parent": {"required_child": "value", "optional_child": "value"},
            "required_top": "value",
        }
        schema = {
            "required_keys": ["required_top"],
            "nested": {"parent": {"required_keys": ["required_child"]}},
        }

        assert loader.validate_schema(config, schema) is True

    def test_validate_schema_nested_missing_key(self, loader):
        """Test validation fails for missing nested required key."""
        config = {"parent": {"optional_child": "value"}}
        schema = {"nested": {"parent": {"required_keys": ["required_child"]}}}

        assert loader.validate_schema(config, schema) is False

    def test_create_example_config(self, loader, temp_dir):
        """Test creating example config file."""
        output_file = temp_dir / "example.yaml"
        template = {
            "key1": "value1",
            "key2": {"nested": "value2"},
        }

        loader.create_example_config(output_file, template)

        assert output_file.exists()
        loaded = loader.load_yaml(output_file)
        assert loaded == template

    def test_create_example_config_exists(self, loader, temp_dir):
        """Test that create_example_config doesn't overwrite existing file."""
        output_file = temp_dir / "existing.yaml"
        output_file.write_text("existing: content")

        template = {"new": "content"}
        loader.create_example_config(output_file, template)

        # Should still have original content
        content = output_file.read_text()
        assert "existing" in content

    def test_get_config_from_env(self, loader):
        """Test extracting config from environment variables."""
        import os

        os.environ["OPSZEN_KEY1"] = "value1"
        os.environ["OPSZEN_KEY2"] = "value2"
        os.environ["OTHER_KEY"] = "other_value"

        config = loader.get_config_from_env(prefix="OPSZEN_")

        assert config["KEY1"] == "value1"
        assert config["KEY2"] == "value2"
        assert "OTHER_KEY" not in config

        # Cleanup
        del os.environ["OPSZEN_KEY1"]
        del os.environ["OPSZEN_KEY2"]
        del os.environ["OTHER_KEY"]

    def test_parse_config_string_simple(self, loader):
        """Test parsing simple config string."""
        config_str = "key1=value1,key2=value2"
        config = loader.parse_config_string(config_str)

        assert config["key1"] == "value1"
        assert config["key2"] == "value2"

    def test_parse_config_string_json_values(self, loader):
        """Test parsing config string with JSON values."""
        config_str = 'key1=123,key2=true,key3={"nested":"value"}'
        config = loader.parse_config_string(config_str)

        assert config["key1"] == 123
        assert config["key2"] is True
        assert config["key3"] == {"nested": "value"}

    def test_parse_config_string_empty(self, loader):
        """Test parsing empty config string."""
        config = loader.parse_config_string("")
        assert config == {}

    def test_parse_config_string_with_spaces(self, loader):
        """Test parsing config string with spaces."""
        config_str = " key1 = value1 , key2 = value2 "
        config = loader.parse_config_string(config_str)

        assert config["key1"] == "value1"
        assert config["key2"] == "value2"

    def test_repr(self, loader):
        """Test string representation."""
        repr_str = repr(loader)
        assert "ConfigLoader" in repr_str
