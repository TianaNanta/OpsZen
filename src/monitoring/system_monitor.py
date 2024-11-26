#!/usr/bin/env python3
import psutil
import time
from datetime import datetime
from rich.console import Console
from rich.table import Table

class SystemMonitor:
    def __init__(self):
        self.console = Console()

    def get_system_metrics(self):
        """Get current system metrics including CPU, memory, and disk usage."""
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory': psutil.virtual_memory()._asdict(),
            'disk': {disk.mountpoint: psutil.disk_usage(disk.mountpoint)._asdict() 
                    for disk in psutil.disk_partitions() if disk.fstype},
            'network': psutil.net_io_counters()._asdict(),
        }

    def display_metrics(self):
        """Display system metrics in a formatted table."""
        metrics = self.get_system_metrics()
        
        table = Table(title="System Metrics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta")
        
        # CPU Usage
        table.add_row("CPU Usage", f"{metrics['cpu_percent']}%")
        
        # Memory Usage
        mem = metrics['memory']
        table.add_row("Memory Total", f"{mem['total'] / (1024**3):.2f} GB")
        table.add_row("Memory Used", f"{mem['used'] / (1024**3):.2f} GB")
        table.add_row("Memory Percent", f"{mem['percent']}%")
        
        # Disk Usage
        for mount, usage in metrics['disk'].items():
            table.add_row(f"Disk {mount} Usage", f"{usage['percent']}%")
        
        # Network I/O
        net = metrics['network']
        table.add_row("Network Bytes Sent", f"{net['bytes_sent'] / (1024**2):.2f} MB")
        table.add_row("Network Bytes Received", f"{net['bytes_recv'] / (1024**2):.2f} MB")
        
        self.console.print(table)

    def monitor_continuously(self, interval=5):
        """Continuously monitor system metrics with specified interval."""
        try:
            while True:
                self.console.clear()
                self.console.print(f"\n[bold green]System Monitor - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/bold green]")
                self.display_metrics()
                time.sleep(interval)
        except KeyboardInterrupt:
            self.console.print("\n[bold red]Monitoring stopped by user[/bold red]")

if __name__ == "__main__":
    monitor = SystemMonitor()
    monitor.monitor_continuously()
