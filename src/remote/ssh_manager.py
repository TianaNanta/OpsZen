#!/usr/bin/env python3
import os
import paramiko
from scp import SCPClient
from typing import List, Dict, Optional, Union
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.progress import Progress

class SSHManager:
    def __init__(self):
        self.console = Console()
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self._load_known_hosts()

    def _load_known_hosts(self):
        """Load known hosts file if it exists."""
        known_hosts = os.path.expanduser('~/.ssh/known_hosts')
        if os.path.exists(known_hosts):
            try:
                self.client.load_host_keys(known_hosts)
            except Exception as e:
                self.console.print(f"[yellow]Warning: Could not load known_hosts: {str(e)}[/yellow]")

    def connect(self, hostname: str, username: str, 
                password: Optional[str] = None, 
                key_filename: Optional[str] = None,
                port: int = 22):
        """Connect to a remote host via SSH."""
        try:
            self.client.connect(
                hostname=hostname,
                username=username,
                password=password,
                key_filename=key_filename,
                port=port
            )
            self.console.print(f"[green]Successfully connected to {username}@{hostname}[/green]")
            return True
        except Exception as e:
            self.console.print(f"[red]Failed to connect: {str(e)}[/red]")
            return False

    def execute_command(self, command: str, sudo: bool = False) -> Dict[str, Union[int, str]]:
        """Execute a command on the remote host."""
        if not self.client.get_transport() or not self.client.get_transport().is_active():
            self.console.print("[red]Not connected to any host[/red]")
            return {"status": -1, "output": "", "error": "Not connected"}

        try:
            if sudo:
                command = f"sudo {command}"
            
            self.console.print(f"[cyan]Executing: {command}[/cyan]")
            stdin, stdout, stderr = self.client.exec_command(command)
            
            exit_status = stdout.channel.recv_exit_status()
            output = stdout.read().decode().strip()
            error = stderr.read().decode().strip()

            if exit_status == 0:
                if output:
                    self.console.print(output)
            else:
                if error:
                    self.console.print(f"[red]Error: {error}[/red]")

            return {
                "status": exit_status,
                "output": output,
                "error": error
            }
        except Exception as e:
            self.console.print(f"[red]Error executing command: {str(e)}[/red]")
            return {"status": -1, "output": "", "error": str(e)}

    def upload_file(self, local_path: str, remote_path: str):
        """Upload a file to the remote host."""
        try:
            with SCPClient(self.client.get_transport()) as scp:
                with Progress() as progress:
                    task = progress.add_task(f"[cyan]Uploading {local_path}...", total=None)
                    scp.put(local_path, remote_path, recursive=True)
                    progress.update(task, completed=100)
            self.console.print(f"[green]Successfully uploaded {local_path} to {remote_path}[/green]")
            return True
        except Exception as e:
            self.console.print(f"[red]Failed to upload file: {str(e)}[/red]")
            return False

    def download_file(self, remote_path: str, local_path: str):
        """Download a file from the remote host."""
        try:
            with SCPClient(self.client.get_transport()) as scp:
                with Progress() as progress:
                    task = progress.add_task(f"[cyan]Downloading {remote_path}...", total=None)
                    scp.get(remote_path, local_path, recursive=True)
                    progress.update(task, completed=100)
            self.console.print(f"[green]Successfully downloaded {remote_path} to {local_path}[/green]")
            return True
        except Exception as e:
            self.console.print(f"[red]Failed to download file: {str(e)}[/red]")
            return False

    def list_directory(self, remote_path: str = "."):
        """List contents of a remote directory."""
        try:
            command = f"ls -la {remote_path}"
            result = self.execute_command(command)
            
            if result["status"] == 0:
                table = Table(title=f"Contents of {remote_path}")
                table.add_column("Permissions", style="cyan")
                table.add_column("Owner", style="green")
                table.add_column("Group", style="green")
                table.add_column("Size", style="magenta")
                table.add_column("Date", style="yellow")
                table.add_column("Name", style="blue")

                # Skip the total line and split into rows
                lines = result["output"].split("\n")[1:]
                for line in lines:
                    parts = line.split(None, 8)
                    if len(parts) >= 9:
                        table.add_row(
                            parts[0],  # permissions
                            parts[2],  # owner
                            parts[3],  # group
                            parts[4],  # size
                            f"{parts[5]} {parts[6]} {parts[7]}",  # date
                            parts[8]   # name
                        )
                
                self.console.print(table)
                return True
        except Exception as e:
            self.console.print(f"[red]Error listing directory: {str(e)}[/red]")
            return False

    def create_directory(self, remote_path: str):
        """Create a directory on the remote host."""
        return self.execute_command(f"mkdir -p {remote_path}")

    def remove_file(self, remote_path: str, recursive: bool = False):
        """Remove a file or directory from the remote host."""
        command = f"rm {'-r' if recursive else ''} {remote_path}"
        return self.execute_command(command)

    def close(self):
        """Close the SSH connection."""
        if self.client:
            self.client.close()
            self.console.print("[yellow]SSH connection closed[/yellow]")
