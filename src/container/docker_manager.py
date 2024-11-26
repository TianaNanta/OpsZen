#!/usr/bin/env python3
import docker
from rich.console import Console
from rich.table import Table
from typing import List, Dict, Optional

class DockerManager:
    def __init__(self):
        self.client = docker.from_env()
        self.console = Console()

    def list_containers(self, all: bool = False) -> List[docker.models.containers.Container]:
        """List all containers."""
        return self.client.containers.list(all=all)

    def display_containers(self, all: bool = False):
        """Display containers in a formatted table."""
        containers = self.list_containers(all)
        
        table = Table(title="Docker Containers")
        table.add_column("Container ID", style="cyan")
        table.add_column("Name", style="magenta")
        table.add_column("Image", style="green")
        table.add_column("Status", style="yellow")
        table.add_column("Ports", style="blue")
        
        for container in containers:
            # Format ports correctly based on the Docker SDK port format
            port_mappings = []
            if container.ports:
                for port_config, mappings in container.ports.items():
                    if mappings:
                        for mapping in mappings:
                            host_port = mapping.get('HostPort', '')
                            port_mappings.append(f"{host_port}->{port_config}")
                    else:
                        port_mappings.append(port_config)
            
            ports = ", ".join(port_mappings) if port_mappings else "None"
            
            table.add_row(
                container.short_id,
                container.name,
                container.image.tags[0] if container.image.tags else "None",
                container.status,
                ports
            )
        
        self.console.print(table)

    def create_container(self, image: str, name: Optional[str] = None, 
                        ports: Optional[Dict] = None, environment: Optional[Dict] = None):
        """Create a new container."""
        try:
            container = self.client.containers.run(
                image,
                name=name,
                ports=ports,
                environment=environment,
                detach=True
            )
            self.console.print(f"[green]Container created successfully: {container.name}[/green]")
            return container
        except docker.errors.APIError as e:
            self.console.print(f"[red]Error creating container: {str(e)}[/red]")
            return None

    def stop_container(self, container_id: str):
        """Stop a running container."""
        try:
            container = self.client.containers.get(container_id)
            container.stop()
            self.console.print(f"[green]Container {container_id} stopped successfully[/green]")
        except docker.errors.NotFound:
            self.console.print(f"[red]Container {container_id} not found[/red]")
        except docker.errors.APIError as e:
            self.console.print(f"[red]Error stopping container: {str(e)}[/red]")

    def remove_container(self, container_id: str, force: bool = False):
        """Remove a container."""
        try:
            container = self.client.containers.get(container_id)
            container.remove(force=force)
            self.console.print(f"[green]Container {container_id} removed successfully[/green]")
        except docker.errors.NotFound:
            self.console.print(f"[red]Container {container_id} not found[/red]")
        except docker.errors.APIError as e:
            self.console.print(f"[red]Error removing container: {str(e)}[/red]")

if __name__ == "__main__":
    manager = DockerManager()
    print("\nListing all running containers:")
    manager.display_containers()
    
    print("\nListing all containers (including stopped):")
    manager.display_containers(all=True)
