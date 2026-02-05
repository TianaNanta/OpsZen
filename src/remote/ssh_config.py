#!/usr/bin/env python3
"""Enhanced SSH configuration manager with support for SSH config files."""

from pathlib import Path
from typing import Dict, List, Optional

import paramiko
from rich.console import Console


class SSHConfig:
    """Manage SSH configuration and connection profiles."""

    def __init__(self):
        self.console = Console()
        self.config = paramiko.SSHConfig()
        self.profiles: Dict[str, Dict] = {}
        self._load_ssh_config()
        self._load_profiles()

    def _load_ssh_config(self):
        """Load SSH configuration from ~/.ssh/config."""
        ssh_config_path = Path.home() / ".ssh" / "config"
        if ssh_config_path.exists():
            try:
                with open(ssh_config_path, "r") as f:
                    self.config.parse(f)
                self.console.print(
                    f"[dim]Loaded SSH config from {ssh_config_path}[/dim]"
                )
            except Exception as e:
                self.console.print(
                    f"[yellow]Warning: Could not load SSH config: {str(e)}[/yellow]"
                )

    def _load_profiles(self):
        """Load connection profiles from OpsZen config."""
        profiles_path = Path.home() / ".opszen" / "ssh_profiles.conf"
        if profiles_path.exists():
            try:
                import configparser

                config = configparser.ConfigParser()
                config.read(profiles_path)

                for section in config.sections():
                    self.profiles[section] = dict(config[section])

                self.console.print(
                    f"[dim]Loaded {len(self.profiles)} profile(s) from {profiles_path}[/dim]"
                )
            except Exception as e:
                self.console.print(
                    f"[yellow]Warning: Could not load profiles: {str(e)}[/yellow]"
                )

    def get_host_config(self, hostname: str) -> Dict:
        """Get SSH configuration for a host."""
        # Try SSH config first
        try:
            host_config = self.config.lookup(hostname)
            return {
                "hostname": host_config.get("hostname", hostname),
                "port": int(host_config.get("port", 22)),
                "user": host_config.get("user"),
                "identityfile": host_config.get("identityfile", [None])[0]
                if "identityfile" in host_config
                else None,
            }
        except Exception:
            return {
                "hostname": hostname,
                "port": 22,
                "user": None,
                "identityfile": None,
            }

    def get_profile(self, profile_name: str) -> Optional[Dict]:
        """Get a saved connection profile."""
        return self.profiles.get(profile_name)

    def save_profile(
        self,
        name: str,
        hostname: str,
        username: str,
        port: int = 22,
        key_file: Optional[str] = None,
    ):
        """Save a connection profile for quick access."""
        profiles_path = Path.home() / ".opszen" / "ssh_profiles.conf"
        profiles_path.parent.mkdir(parents=True, exist_ok=True)

        import configparser

        config = configparser.ConfigParser()
        if profiles_path.exists():
            config.read(profiles_path)

        if name not in config.sections():
            config.add_section(name)

        config[name]["hostname"] = hostname
        config[name]["username"] = username
        config[name]["port"] = str(port)
        if key_file:
            config[name]["key_file"] = key_file

        with open(profiles_path, "w") as f:
            config.write(f)

        self.profiles[name] = {
            "hostname": hostname,
            "username": username,
            "port": str(port),
            "key_file": key_file,
        }

        self.console.print(f"[green]Profile '{name}' saved successfully[/green]")

    def list_profiles(self):
        """List all saved connection profiles."""
        if not self.profiles:
            self.console.print("[yellow]No saved profiles found[/yellow]")
            return

        from rich.table import Table

        table = Table(title="SSH Connection Profiles")
        table.add_column("Name", style="cyan")
        table.add_column("Hostname", style="green")
        table.add_column("Username", style="yellow")
        table.add_column("Port", style="blue")

        for name, profile in self.profiles.items():
            table.add_row(
                name,
                profile.get("hostname", ""),
                profile.get("username", ""),
                profile.get("port", "22"),
            )

        self.console.print(table)

    def delete_profile(self, name: str):
        """Delete a connection profile."""
        if name not in self.profiles:
            self.console.print(f"[red]Profile '{name}' not found[/red]")
            return

        profiles_path = Path.home() / ".opszen" / "ssh_profiles.conf"

        import configparser

        config = configparser.ConfigParser()
        if profiles_path.exists():
            config.read(profiles_path)
            if name in config.sections():
                config.remove_section(name)
                with open(profiles_path, "w") as f:
                    config.write(f)

        del self.profiles[name]
        self.console.print(f"[green]Profile '{name}' deleted[/green]")

    def find_key_files(self) -> List[str]:
        """Find available SSH key files."""
        ssh_dir = Path.home() / ".ssh"
        if not ssh_dir.exists():
            return []

        key_files = []
        common_keys = ["id_rsa", "id_ed25519", "id_ecdsa", "id_dsa"]

        for key_name in common_keys:
            key_path = ssh_dir / key_name
            if key_path.exists():
                key_files.append(str(key_path))

        return key_files

    def get_default_key(self) -> Optional[str]:
        """Get the default SSH key file."""
        keys = self.find_key_files()
        if keys:
            # Prefer ed25519, then rsa
            for key in keys:
                if "ed25519" in key:
                    return key
            return keys[0]
        return None
