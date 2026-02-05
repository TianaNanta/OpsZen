#!/usr/bin/env python3
import os
from pathlib import Path
from typing import Dict, Optional, Union

import paramiko
from rich.console import Console
from rich.progress import Progress
from rich.table import Table
from scp import SCPClient

from .ssh_config import SSHConfig


class SSHManager:
    def __init__(self):
        self.console = Console()
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.config = SSHConfig()
        self._load_known_hosts()
        self.current_host = None
        self.current_user = None

    def _load_known_hosts(self):
        """Load known hosts file if it exists."""
        known_hosts = os.path.expanduser("~/.ssh/known_hosts")
        if os.path.exists(known_hosts):
            try:
                self.client.load_host_keys(known_hosts)
            except Exception as e:
                self.console.print(
                    f"[yellow]Warning: Could not load known_hosts: {str(e)}[/yellow]"
                )

    def connect(
        self,
        hostname: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        key_filename: Optional[str] = None,
        port: Optional[int] = None,
    ):
        """Connect to a remote host via SSH with smart defaults."""
        # Check if it's a saved profile
        profile = self.config.get_profile(hostname)
        if profile:
            self.console.print(f"[cyan]Using saved profile: {hostname}[/cyan]")
            hostname = profile.get("hostname", hostname)
            username = username or profile.get("username")
            port = port or int(profile.get("port", 22))
            key_filename = key_filename or profile.get("key_file")

        # Get SSH config if available
        host_config = self.config.get_host_config(hostname)
        hostname = host_config.get("hostname", hostname)
        username = username or host_config.get("user") or os.getenv("USER")
        port = port or host_config.get("port", 22)

        # Smart key file detection
        if not key_filename and not password:
            key_filename = (
                host_config.get("identityfile") or self.config.get_default_key()
            )
            if key_filename:
                self.console.print(f"[dim]Using key: {Path(key_filename).name}[/dim]")

        try:
            connect_kwargs = {
                "hostname": hostname,
                "username": username,
                "port": port,
            }

            if password:
                connect_kwargs["password"] = password
            elif key_filename:
                connect_kwargs["key_filename"] = key_filename

            self.client.connect(**connect_kwargs)
            self.current_host = hostname
            self.current_user = username
            self.console.print(
                f"[green]✓ Connected to {username}@{hostname}:{port}[/green]"
            )
            return True
        except Exception as e:
            self.console.print(f"[red]✗ Connection failed: {str(e)}[/red]")
            return False

    def execute_command(
        self, command: str, sudo: bool = False
    ) -> Dict[str, Union[int, str]]:
        """Execute a command on the remote host."""
        transport = self.client.get_transport()
        if not transport or not transport.is_active():
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

            return {"status": exit_status, "output": output, "error": error}
        except Exception as e:
            self.console.print(f"[red]Error executing command: {str(e)}[/red]")
            return {"status": -1, "output": "", "error": str(e)}

    def upload_file(self, local_path: str, remote_path: str):
        """Upload a file to the remote host."""
        try:
            transport = self.client.get_transport()
            if transport is None:
                self.console.print("[red]Not connected to any host[/red]")
                return False
            with SCPClient(transport) as scp:
                with Progress() as progress:
                    task = progress.add_task(
                        f"[cyan]Uploading {local_path}...", total=None
                    )
                    scp.put(local_path, remote_path, recursive=True)
                    progress.update(task, completed=100)
            self.console.print(
                f"[green]Successfully uploaded {local_path} to {remote_path}[/green]"
            )
            return True
        except Exception as e:
            self.console.print(f"[red]Failed to upload file: {str(e)}[/red]")
            return False

    def download_file(self, remote_path: str, local_path: str):
        """Download a file from the remote host."""
        try:
            transport = self.client.get_transport()
            if transport is None:
                self.console.print("[red]Not connected to any host[/red]")
                return False
            with SCPClient(transport) as scp:
                with Progress() as progress:
                    task = progress.add_task(
                        f"[cyan]Downloading {remote_path}...", total=None
                    )
                    scp.get(remote_path, local_path, recursive=True)
                    progress.update(task, completed=100)
            self.console.print(
                f"[green]Successfully downloaded {remote_path} to {local_path}[/green]"
            )
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
                output = str(result["output"])
                lines = output.split("\n")[1:]
                for line in lines:
                    parts = line.split(None, 8)
                    if len(parts) >= 9:
                        table.add_row(
                            parts[0],  # permissions
                            parts[2],  # owner
                            parts[3],  # group
                            parts[4],  # size
                            f"{parts[5]} {parts[6]} {parts[7]}",  # date
                            parts[8],  # name
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
            if self.current_host:
                self.console.print(
                    f"[yellow]✓ Disconnected from {self.current_user}@{self.current_host}[/yellow]"
                )
            self.current_host = None
            self.current_user = None

    def run_script(
        self, script_path: str, sudo: bool = False
    ) -> Dict[str, Union[int, str]]:
        """Execute a local script on the remote host."""
        try:
            with open(script_path, "r") as f:
                script_content = f.read()

            self.console.print(f"[cyan]Executing script: {script_path}[/cyan]")
            return self.execute_command(script_content, sudo=sudo)
        except FileNotFoundError:
            self.console.print(f"[red]Script not found: {script_path}[/red]")
            return {"status": -1, "output": "", "error": "Script not found"}
        except Exception as e:
            self.console.print(f"[red]Error reading script: {str(e)}[/red]")
            return {"status": -1, "output": "", "error": str(e)}

    def interactive_shell(self):
        """Start an interactive shell session."""
        transport = self.client.get_transport()
        if not transport or not transport.is_active():
            self.console.print("[red]Not connected to any host[/red]")
            return

        try:
            channel = transport.open_session()
            channel.get_pty()
            channel.invoke_shell()

            self.console.print(
                f"[green]Interactive shell started on {self.current_user}@{self.current_host}[/green]"
            )
            self.console.print("[dim]Type 'exit' to close the session[/dim]\n")

            import select
            import sys

            while True:
                r, w, e = select.select([channel, sys.stdin], [], [])
                if channel in r:
                    try:
                        data = channel.recv(1024)
                        if len(data) == 0:
                            break
                        sys.stdout.write(data.decode("utf-8", errors="ignore"))
                        sys.stdout.flush()
                    except Exception:
                        break

                if sys.stdin in r:
                    data = sys.stdin.read(1)
                    if len(data) == 0:
                        break
                    channel.send(data.encode("utf-8"))

            channel.close()
            self.console.print("\n[yellow]Interactive shell closed[/yellow]")

        except Exception as e:
            self.console.print(f"[red]Shell error: {str(e)}[/red]")
