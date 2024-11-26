#!/usr/bin/env python3
import typer
from typing import Optional
from pathlib import Path
from rich.console import Console
from .monitoring.system_monitor import SystemMonitor
from .container.docker_manager import DockerManager
from .logs.log_analyzer import LogAnalyzer
from .infrastructure.provisioner import InfrastructureProvisioner
from .remote.ssh_manager import SSHManager

app = typer.Typer(help="OpsZen - A comprehensive toolkit for system monitoring, container management, and more.")
console = Console()

# Create sub-applications for each module
monitor_app = typer.Typer(help="System monitoring commands")
docker_app = typer.Typer(help="Docker container management commands")
logs_app = typer.Typer(help="Log analysis commands")
infra_app = typer.Typer(help="Infrastructure provisioning commands")
ssh_app = typer.Typer(help="SSH remote management commands")

app.add_typer(monitor_app, name="monitor")
app.add_typer(docker_app, name="docker")
app.add_typer(logs_app, name="logs")
app.add_typer(infra_app, name="infra")
app.add_typer(ssh_app, name="ssh")

# System Monitoring Commands
@monitor_app.command("start")
def start_monitoring(
    interval: int = typer.Option(5, help="Monitoring interval in seconds"),
):
    """Start continuous system monitoring."""
    monitor = SystemMonitor()
    console.print(f"[green]Starting system monitoring (interval: {interval}s)...[/green]")
    monitor.monitor_continuously(interval)

@monitor_app.command("snapshot")
def system_snapshot():
    """Take a snapshot of current system metrics."""
    monitor = SystemMonitor()
    monitor.display_metrics()

# Docker Commands
@docker_app.command("list")
def list_containers(
    all: bool = typer.Option(False, "--all", "-a", help="Show all containers including stopped ones")
):
    """List Docker containers."""
    docker = DockerManager()
    docker.display_containers(all=all)

@docker_app.command("create")
def create_container(
    image: str = typer.Argument(..., help="Docker image name"),
    name: str = typer.Option(None, "--name", "-n", help="Container name"),
    port: str = typer.Option(None, "--port", "-p", help="Port mapping (host:container)"),
):
    """Create a new Docker container."""
    docker = DockerManager()
    ports = {}
    if port:
        host_port, container_port = port.split(":")
        ports = {container_port: host_port}
    docker.create_container(image, name=name, ports=ports)

@docker_app.command("stop")
def stop_container(
    container_id: str = typer.Argument(..., help="Container ID or name")
):
    """Stop a running container."""
    docker = DockerManager()
    docker.stop_container(container_id)

@docker_app.command("remove")
def remove_container(
    container_id: str = typer.Argument(..., help="Container ID or name"),
    force: bool = typer.Option(False, "--force", "-f", help="Force remove running container")
):
    """Remove a container."""
    docker = DockerManager()
    docker.remove_container(container_id, force=force)

# Log Analysis Commands
@logs_app.command("analyze")
def analyze_logs(
    file_path: Path = typer.Argument(..., help="Path to log file", exists=True)
):
    """Analyze a log file and show statistics."""
    analyzer = LogAnalyzer()
    analyzer.analyze_logs(str(file_path))

@logs_app.command("filter")
def filter_logs(
    file_path: Path = typer.Argument(..., help="Path to log file", exists=True),
    level: str = typer.Option(None, "--level", "-l", help="Filter by log level (ERROR, WARNING, INFO)"),
    start_time: str = typer.Option(None, "--start", help="Start time (YYYY-MM-DD HH:MM:SS)"),
    end_time: str = typer.Option(None, "--end", help="End time (YYYY-MM-DD HH:MM:SS)")
):
    """Filter logs based on criteria."""
    analyzer = LogAnalyzer()
    analyzer.filter_logs(str(file_path), level=level, start_time=start_time, end_time=end_time)

# Infrastructure Commands
@infra_app.command("list-ec2")
def list_ec2():
    """List EC2 instances."""
    provisioner = InfrastructureProvisioner()
    provisioner.list_instances()

@infra_app.command("list-s3")
def list_s3():
    """List S3 buckets."""
    provisioner = InfrastructureProvisioner()
    provisioner.list_s3_buckets()

@infra_app.command("create-ec2")
def create_ec2(
    name: str = typer.Option(..., help="Instance name"),
    image_id: str = typer.Option(..., help="AMI ID"),
    instance_type: str = typer.Option("t2.micro", help="Instance type"),
    key_name: str = typer.Option(None, help="Key pair name"),
):
    """Create an EC2 instance."""
    provisioner = InfrastructureProvisioner()
    config = {
        "name": name,
        "image_id": image_id,
        "instance_type": instance_type,
        "key_name": key_name
    }
    provisioner.create_ec2_instance(config)

@infra_app.command("create-s3")
def create_s3(
    name: str = typer.Argument(..., help="Bucket name"),
    region: str = typer.Option("us-west-2", help="AWS region")
):
    """Create an S3 bucket."""
    provisioner = InfrastructureProvisioner()
    provisioner.create_s3_bucket(name, region)

@infra_app.command("provision")
def provision_infrastructure(
    config_file: Path = typer.Argument(..., help="YAML configuration file", exists=True)
):
    """Provision infrastructure from YAML configuration."""
    provisioner = InfrastructureProvisioner()
    provisioner.provision_from_yaml(str(config_file))

# SSH Commands
@ssh_app.command("connect")
def ssh_connect(
    host: str = typer.Argument(..., help="Remote host to connect to"),
    username: str = typer.Argument(..., help="SSH username"),
    password: str = typer.Option(None, "--password", "-p", help="SSH password"),
    key_file: Path = typer.Option(None, "--key", "-k", help="SSH private key file"),
    port: int = typer.Option(22, help="SSH port")
):
    """Connect to a remote host via SSH."""
    ssh = SSHManager()
    ssh.connect(host, username, password, str(key_file) if key_file else None, port)
    return ssh

@ssh_app.command("execute")
def ssh_execute(
    host: str = typer.Argument(..., help="Remote host to connect to"),
    username: str = typer.Argument(..., help="SSH username"),
    command: str = typer.Argument(..., help="Command to execute"),
    password: str = typer.Option(None, "--password", "-p", help="SSH password"),
    key_file: Path = typer.Option(None, "--key", "-k", help="SSH private key file"),
    sudo: bool = typer.Option(False, "--sudo", "-s", help="Execute with sudo"),
):
    """Execute a command on a remote host."""
    ssh = SSHManager()
    if ssh.connect(host, username, password, str(key_file) if key_file else None):
        ssh.execute_command(command, sudo=sudo)
        ssh.close()

@ssh_app.command("upload")
def ssh_upload(
    host: str = typer.Argument(..., help="Remote host to connect to"),
    username: str = typer.Argument(..., help="SSH username"),
    local_path: Path = typer.Argument(..., help="Local file or directory to upload"),
    remote_path: str = typer.Argument(..., help="Remote destination path"),
    password: str = typer.Option(None, "--password", "-p", help="SSH password"),
    key_file: Path = typer.Option(None, "--key", "-k", help="SSH private key file"),
):
    """Upload a file or directory to a remote host."""
    ssh = SSHManager()
    if ssh.connect(host, username, password, str(key_file) if key_file else None):
        ssh.upload_file(str(local_path), remote_path)
        ssh.close()

@ssh_app.command("download")
def ssh_download(
    host: str = typer.Argument(..., help="Remote host to connect to"),
    username: str = typer.Argument(..., help="SSH username"),
    remote_path: str = typer.Argument(..., help="Remote file or directory to download"),
    local_path: Path = typer.Argument(..., help="Local destination path"),
    password: str = typer.Option(None, "--password", "-p", help="SSH password"),
    key_file: Path = typer.Option(None, "--key", "-k", help="SSH private key file"),
):
    """Download a file or directory from a remote host."""
    ssh = SSHManager()
    if ssh.connect(host, username, password, str(key_file) if key_file else None):
        ssh.download_file(remote_path, str(local_path))
        ssh.close()

@ssh_app.command("ls")
def ssh_list(
    host: str = typer.Argument(..., help="Remote host to connect to"),
    username: str = typer.Argument(..., help="SSH username"),
    remote_path: str = typer.Argument(".", help="Remote path to list"),
    password: str = typer.Option(None, "--password", "-p", help="SSH password"),
    key_file: Path = typer.Option(None, "--key", "-k", help="SSH private key file"),
):
    """List contents of a remote directory."""
    ssh = SSHManager()
    if ssh.connect(host, username, password, str(key_file) if key_file else None):
        ssh.list_directory(remote_path)
        ssh.close()

if __name__ == "__main__":
    app()
