#!/usr/bin/env python3
"""
Unit tests for DockerManager module.
"""

from unittest.mock import MagicMock, patch

try:
    import docker
    import docker.errors
except ImportError:
    docker = None

try:
    import pytest
except ImportError:
    pytest = None

from src.container.docker_manager import DockerManager


class TestDockerManager:
    """Test suite for DockerManager class."""

    @pytest.fixture
    def docker_manager(self, mock_docker_client):
        """Create a DockerManager instance with mocked Docker client."""
        with patch("docker.from_env") as mock_from_env:
            mock_from_env.return_value = mock_docker_client
            manager = DockerManager()
            yield manager

    def test_initialization(self, mock_docker_client):
        """Test DockerManager initialization."""
        with patch("docker.from_env") as mock_from_env:
            mock_from_env.return_value = mock_docker_client
            manager = DockerManager()
            assert manager is not None
            assert manager.client == mock_docker_client

    def test_list_containers_running_only(self, docker_manager, mock_docker_client):
        """Test listing only running containers."""
        containers = docker_manager.list_containers(all=False)

        assert len(containers) == 1
        assert containers[0].name == "test_container_1"
        mock_docker_client.containers.list.assert_called()

    def test_list_containers_all(self, docker_manager, mock_docker_client):
        """Test listing all containers including stopped."""
        containers = docker_manager.list_containers(all=True)

        assert len(containers) == 2
        mock_docker_client.containers.list.assert_called_with(all=True)

    def test_display_containers_running(self, docker_manager, mock_docker_client):
        """Test displaying running containers in table format."""
        # Should not raise any exceptions
        docker_manager.display_containers(all=False)
        mock_docker_client.containers.list.assert_called()

    def test_display_containers_all(self, docker_manager, mock_docker_client):
        """Test displaying all containers in table format."""
        # Should not raise any exceptions
        docker_manager.display_containers(all=True)
        mock_docker_client.containers.list.assert_called()

    def test_display_containers_with_ports(self, docker_manager, mock_docker_client):
        """Test displaying containers with port mappings."""
        mock_container = MagicMock()
        mock_container.short_id = "abc123"
        mock_container.name = "web_server"
        mock_container.status = "running"
        mock_container.image.tags = ["nginx:latest"]
        mock_container.ports = {
            "80/tcp": [{"HostPort": "8080"}],
            "443/tcp": [{"HostPort": "8443"}],
        }

        mock_docker_client.containers.list.return_value = [mock_container]

        # Should handle multiple port mappings
        docker_manager.display_containers()

    def test_display_containers_no_ports(self, docker_manager, mock_docker_client):
        """Test displaying containers with no port mappings."""
        mock_container = MagicMock()
        mock_container.short_id = "def456"
        mock_container.name = "worker"
        mock_container.status = "running"
        mock_container.image.tags = ["worker:latest"]
        mock_container.ports = {}

        mock_docker_client.containers.list.return_value = [mock_container]

        # Should handle containers with no ports
        docker_manager.display_containers()

    def test_display_containers_no_image_tags(self, docker_manager, mock_docker_client):
        """Test displaying containers with no image tags."""
        mock_container = MagicMock()
        mock_container.short_id = "ghi789"
        mock_container.name = "unnamed"
        mock_container.status = "running"
        mock_container.image.tags = []
        mock_container.ports = {}

        mock_docker_client.containers.list.return_value = [mock_container]

        # Should handle containers with no image tags
        docker_manager.display_containers()

    def test_create_container_basic(self, docker_manager, mock_docker_client):
        """Test creating a basic container."""
        mock_container = MagicMock()
        mock_container.name = "new_container"
        mock_docker_client.containers.run.return_value = mock_container

        result = docker_manager.create_container("nginx:latest", name="new_container")

        assert result == mock_container
        mock_docker_client.containers.run.assert_called_once()

    def test_create_container_with_ports(self, docker_manager, mock_docker_client):
        """Test creating container with port mappings."""
        mock_container = MagicMock()
        mock_container.name = "web_app"
        mock_docker_client.containers.run.return_value = mock_container

        ports = {"80/tcp": 8080, "443/tcp": 8443}
        result = docker_manager.create_container(
            "nginx:latest", name="web_app", ports=ports
        )

        assert result == mock_container
        call_args = mock_docker_client.containers.run.call_args
        assert call_args[1]["ports"] == ports

    def test_create_container_with_environment(
        self, docker_manager, mock_docker_client
    ):
        """Test creating container with environment variables."""
        mock_container = MagicMock()
        mock_container.name = "app"
        mock_docker_client.containers.run.return_value = mock_container

        env = {"DATABASE_URL": "postgres://localhost", "DEBUG": "true"}
        result = docker_manager.create_container(
            "myapp:latest", name="app", environment=env
        )

        assert result == mock_container
        call_args = mock_docker_client.containers.run.call_args
        assert call_args[1]["environment"] == env

    def test_create_container_detached(self, docker_manager, mock_docker_client):
        """Test that containers are created in detached mode."""
        mock_container = MagicMock()
        mock_docker_client.containers.run.return_value = mock_container

        docker_manager.create_container("nginx:latest")

        call_args = mock_docker_client.containers.run.call_args
        assert call_args[1]["detach"] is True

    def test_create_container_api_error(self, docker_manager, mock_docker_client):
        """Test handling Docker API error during container creation."""
        from docker.errors import APIError

        mock_docker_client.containers.run.side_effect = APIError("Image not found")

        result = docker_manager.create_container("nonexistent:latest")

        assert result is None

    def test_stop_container_success(self, docker_manager, mock_docker_client):
        """Test stopping a container successfully."""
        mock_container = MagicMock()
        mock_docker_client.containers.get.return_value = mock_container

        docker_manager.stop_container("abc123")

        mock_docker_client.containers.get.assert_called_once_with("abc123")
        mock_container.stop.assert_called_once()

    def test_stop_container_not_found(self, docker_manager, mock_docker_client):
        """Test stopping a non-existent container."""
        from docker.errors import NotFound

        mock_docker_client.containers.get.side_effect = NotFound("Container not found")

        # Should handle gracefully without raising exception
        docker_manager.stop_container("nonexistent")

    def test_stop_container_api_error(self, docker_manager, mock_docker_client):
        """Test handling API error when stopping container."""
        from docker.errors import APIError

        mock_container = MagicMock()
        mock_container.stop.side_effect = APIError("Error stopping")
        mock_docker_client.containers.get.return_value = mock_container

        # Should handle gracefully
        docker_manager.stop_container("abc123")

    def test_remove_container_success(self, docker_manager, mock_docker_client):
        """Test removing a container successfully."""
        mock_container = MagicMock()
        mock_docker_client.containers.get.return_value = mock_container

        docker_manager.remove_container("abc123")

        mock_docker_client.containers.get.assert_called_once_with("abc123")
        mock_container.remove.assert_called_once_with(force=False)

    def test_remove_container_force(self, docker_manager, mock_docker_client):
        """Test force removing a container."""
        mock_container = MagicMock()
        mock_docker_client.containers.get.return_value = mock_container

        docker_manager.remove_container("abc123", force=True)

        mock_container.remove.assert_called_once_with(force=True)

    def test_remove_container_not_found(self, docker_manager, mock_docker_client):
        """Test removing a non-existent container."""
        from docker.errors import NotFound

        mock_docker_client.containers.get.side_effect = NotFound("Container not found")

        # Should handle gracefully
        docker_manager.remove_container("nonexistent")

    def test_remove_container_api_error(self, docker_manager, mock_docker_client):
        """Test handling API error when removing container."""
        from docker.errors import APIError

        mock_container = MagicMock()
        mock_container.remove.side_effect = APIError("Error removing")
        mock_docker_client.containers.get.return_value = mock_container

        # Should handle gracefully
        docker_manager.remove_container("abc123")

    def test_list_containers_empty(self, docker_manager, mock_docker_client):
        """Test listing containers when none exist."""
        # Reset the side_effect from conftest.py and set return_value
        mock_docker_client.containers.list.side_effect = None
        mock_docker_client.containers.list.return_value = []

        containers = docker_manager.list_containers()

        assert containers == []

    def test_display_containers_empty(self, docker_manager, mock_docker_client):
        """Test displaying containers when none exist."""
        mock_docker_client.containers.list.return_value = []

        # Should handle empty list gracefully
        docker_manager.display_containers()

    def test_create_container_full_config(self, docker_manager, mock_docker_client):
        """Test creating container with full configuration."""
        mock_container = MagicMock()
        mock_container.name = "full_config_app"
        mock_docker_client.containers.run.return_value = mock_container

        result = docker_manager.create_container(
            image="myapp:v1.0",
            name="full_config_app",
            ports={"8000/tcp": 8000},
            environment={"ENV": "production", "LOG_LEVEL": "info"},
        )

        assert result == mock_container
        call_args = mock_docker_client.containers.run.call_args
        assert call_args[0][0] == "myapp:v1.0"
        assert call_args[1]["name"] == "full_config_app"
        assert call_args[1]["ports"] == {"8000/tcp": 8000}
        assert call_args[1]["environment"]["ENV"] == "production"

    def test_container_ports_format_multiple(self, docker_manager, mock_docker_client):
        """Test handling containers with multiple port mappings per port."""
        mock_container = MagicMock()
        mock_container.short_id = "xyz123"
        mock_container.name = "multi_port"
        mock_container.status = "running"
        mock_container.image.tags = ["app:latest"]
        mock_container.ports = {
            "80/tcp": [{"HostPort": "8080"}, {"HostPort": "8081"}],
        }

        mock_docker_client.containers.list.return_value = [mock_container]

        # Should handle multiple mappings for same port
        docker_manager.display_containers()

    def test_container_ports_format_none_mapping(
        self, docker_manager, mock_docker_client
    ):
        """Test handling containers with exposed but unmapped ports."""
        mock_container = MagicMock()
        mock_container.short_id = "uvw456"
        mock_container.name = "exposed_port"
        mock_container.status = "running"
        mock_container.image.tags = ["app:latest"]
        mock_container.ports = {"80/tcp": None}

        mock_docker_client.containers.list.return_value = [mock_container]

        # Should handle None port mappings
        docker_manager.display_containers()

    def test_stop_multiple_containers(self, docker_manager, mock_docker_client):
        """Test stopping multiple containers sequentially."""
        mock_container1 = MagicMock()
        mock_container2 = MagicMock()

        mock_docker_client.containers.get.side_effect = [
            mock_container1,
            mock_container2,
        ]

        docker_manager.stop_container("container1")
        docker_manager.stop_container("container2")

        assert mock_docker_client.containers.get.call_count == 2
        mock_container1.stop.assert_called_once()
        mock_container2.stop.assert_called_once()

    def test_remove_multiple_containers(self, docker_manager, mock_docker_client):
        """Test removing multiple containers sequentially."""
        mock_container1 = MagicMock()
        mock_container2 = MagicMock()

        mock_docker_client.containers.get.side_effect = [
            mock_container1,
            mock_container2,
        ]

        docker_manager.remove_container("container1")
        docker_manager.remove_container("container2")

        assert mock_docker_client.containers.get.call_count == 2
        mock_container1.remove.assert_called_once()
        mock_container2.remove.assert_called_once()
