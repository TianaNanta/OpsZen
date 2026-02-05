#!/usr/bin/env python3
"""
Unit tests for SystemMonitor module.
"""

from unittest.mock import MagicMock, patch

import pytest

from src.monitoring.system_monitor import SystemMonitor


class TestSystemMonitor:
    """Test suite for SystemMonitor class."""

    @pytest.fixture
    def system_monitor(self):
        """Create a SystemMonitor instance."""
        return SystemMonitor()

    def test_initialization(self, system_monitor):
        """Test SystemMonitor initialization."""
        assert system_monitor is not None
        assert system_monitor.console is not None

    def test_get_system_metrics(self, system_monitor, mock_psutil):
        """Test getting system metrics."""
        metrics = system_monitor.get_system_metrics()

        assert "cpu_percent" in metrics
        assert "memory" in metrics
        assert "disk" in metrics
        assert "network" in metrics

        assert metrics["cpu_percent"] == 45.5
        assert metrics["memory"]["percent"] == 50.0
        assert metrics["network"]["bytes_sent"] == 1024 * 1024 * 100

    def test_get_system_metrics_cpu(self, system_monitor, mock_psutil):
        """Test CPU metrics extraction."""
        metrics = system_monitor.get_system_metrics()

        assert isinstance(metrics["cpu_percent"], float)
        assert 0 <= metrics["cpu_percent"] <= 100

    def test_get_system_metrics_memory(self, system_monitor, mock_psutil):
        """Test memory metrics extraction."""
        metrics = system_monitor.get_system_metrics()

        assert "total" in metrics["memory"]
        assert "available" in metrics["memory"]
        assert "used" in metrics["memory"]
        assert "percent" in metrics["memory"]

        assert metrics["memory"]["total"] == 16 * 1024**3
        assert metrics["memory"]["used"] == 8 * 1024**3
        assert metrics["memory"]["percent"] == 50.0

    def test_get_system_metrics_disk(self, system_monitor, mock_psutil):
        """Test disk metrics extraction."""
        metrics = system_monitor.get_system_metrics()

        assert "/" in metrics["disk"]
        disk_usage = metrics["disk"]["/"]

        assert "total" in disk_usage
        assert "used" in disk_usage
        assert "free" in disk_usage
        assert "percent" in disk_usage

        assert disk_usage["total"] == 500 * 1024**3
        assert disk_usage["percent"] == 50.0

    def test_get_system_metrics_network(self, system_monitor, mock_psutil):
        """Test network metrics extraction."""
        metrics = system_monitor.get_system_metrics()

        assert "bytes_sent" in metrics["network"]
        assert "bytes_recv" in metrics["network"]

        assert metrics["network"]["bytes_sent"] == 1024 * 1024 * 100
        assert metrics["network"]["bytes_recv"] == 1024 * 1024 * 200

    def test_display_metrics(self, system_monitor, mock_psutil):
        """Test displaying metrics in table format."""
        # Should not raise any exceptions
        system_monitor.display_metrics()

    def test_display_metrics_formatting(self, system_monitor, mock_psutil):
        """Test that display_metrics formats values correctly."""
        with patch.object(system_monitor.console, "print") as mock_print:
            system_monitor.display_metrics()
            # Verify that console.print was called
            assert mock_print.called

    def test_get_system_metrics_multiple_disks(self, system_monitor):
        """Test handling multiple disk partitions."""
        with patch("psutil.cpu_percent") as mock_cpu, patch(
            "psutil.virtual_memory"
        ) as mock_mem, patch("psutil.disk_usage") as mock_disk, patch(
            "psutil.disk_partitions"
        ) as mock_partitions, patch("psutil.net_io_counters") as mock_net:
            # Setup mocks
            mock_cpu.return_value = 50.0

            mock_mem.return_value = MagicMock(
                total=16 * 1024**3,
                available=8 * 1024**3,
                used=8 * 1024**3,
                percent=50.0,
            )
            mock_mem.return_value._asdict.return_value = {
                "total": 16 * 1024**3,
                "available": 8 * 1024**3,
                "used": 8 * 1024**3,
                "percent": 50.0,
            }

            # Multiple partitions
            partition1 = MagicMock()
            partition1.mountpoint = "/"
            partition1.fstype = "ext4"

            partition2 = MagicMock()
            partition2.mountpoint = "/home"
            partition2.fstype = "ext4"

            mock_partitions.return_value = [partition1, partition2]

            def disk_usage_side_effect(path):
                usage = MagicMock(
                    total=500 * 1024**3,
                    used=250 * 1024**3,
                    free=250 * 1024**3,
                    percent=50.0,
                )
                usage._asdict.return_value = {
                    "total": 500 * 1024**3,
                    "used": 250 * 1024**3,
                    "free": 250 * 1024**3,
                    "percent": 50.0,
                }
                return usage

            mock_disk.side_effect = disk_usage_side_effect

            mock_net.return_value = MagicMock(
                bytes_sent=1024 * 1024 * 100, bytes_recv=1024 * 1024 * 200
            )
            mock_net.return_value._asdict.return_value = {
                "bytes_sent": 1024 * 1024 * 100,
                "bytes_recv": 1024 * 1024 * 200,
            }

            metrics = system_monitor.get_system_metrics()

            assert "/" in metrics["disk"]
            assert "/home" in metrics["disk"]

    def test_get_system_metrics_no_filesystem(self, system_monitor):
        """Test handling partitions with no filesystem."""
        with patch("psutil.cpu_percent") as mock_cpu, patch(
            "psutil.virtual_memory"
        ) as mock_mem, patch("psutil.disk_usage") as mock_disk, patch(
            "psutil.disk_partitions"
        ) as mock_partitions, patch("psutil.net_io_counters") as mock_net:
            mock_cpu.return_value = 50.0

            mock_mem.return_value = MagicMock(percent=50.0)
            mock_mem.return_value._asdict.return_value = {"percent": 50.0}

            # Partition with no fstype (should be skipped)
            partition_no_fs = MagicMock()
            partition_no_fs.mountpoint = "/dev/sda1"
            partition_no_fs.fstype = ""

            partition_valid = MagicMock()
            partition_valid.mountpoint = "/"
            partition_valid.fstype = "ext4"

            mock_partitions.return_value = [partition_no_fs, partition_valid]

            mock_disk.return_value = MagicMock(percent=50.0)
            mock_disk.return_value._asdict.return_value = {"percent": 50.0}

            mock_net.return_value = MagicMock(bytes_sent=0, bytes_recv=0)
            mock_net.return_value._asdict.return_value = {
                "bytes_sent": 0,
                "bytes_recv": 0,
            }

            metrics = system_monitor.get_system_metrics()

            # Should only have the valid partition
            assert "/" in metrics["disk"]
            assert "/dev/sda1" not in metrics["disk"]

    def test_monitor_continuously_keyboard_interrupt(self, system_monitor, mock_psutil):
        """Test continuous monitoring stops on KeyboardInterrupt."""
        with patch("time.sleep") as mock_sleep:
            # Simulate KeyboardInterrupt after first iteration
            mock_sleep.side_effect = KeyboardInterrupt()

            # Should handle KeyboardInterrupt gracefully
            system_monitor.monitor_continuously(interval=1)

    def test_monitor_continuously_interval(self, system_monitor, mock_psutil):
        """Test continuous monitoring respects interval."""
        with patch("time.sleep") as mock_sleep, patch.object(
            system_monitor.console, "clear"
        ):
            # Raise KeyboardInterrupt after first sleep
            mock_sleep.side_effect = KeyboardInterrupt()

            system_monitor.monitor_continuously(interval=10)

            # Verify sleep was called with correct interval
            mock_sleep.assert_called_with(10)

    def test_monitor_continuously_clears_console(self, system_monitor, mock_psutil):
        """Test continuous monitoring clears console."""
        with patch("time.sleep") as mock_sleep, patch.object(
            system_monitor.console, "clear"
        ) as mock_clear:
            mock_sleep.side_effect = KeyboardInterrupt()

            system_monitor.monitor_continuously()

            # Verify console was cleared
            assert mock_clear.called

    def test_display_metrics_cpu_formatting(self, system_monitor, mock_psutil):
        """Test CPU metric is displayed with percentage."""
        metrics = system_monitor.get_system_metrics()
        assert metrics["cpu_percent"] == 45.5

        # Display should format this correctly
        system_monitor.display_metrics()

    def test_display_metrics_memory_gb_conversion(self, system_monitor, mock_psutil):
        """Test memory metrics are converted to GB."""
        metrics = system_monitor.get_system_metrics()

        # 16 GB total
        total_gb = metrics["memory"]["total"] / (1024**3)
        assert total_gb == 16.0

        # 8 GB used
        used_gb = metrics["memory"]["used"] / (1024**3)
        assert used_gb == 8.0

    def test_display_metrics_network_mb_conversion(self, system_monitor, mock_psutil):
        """Test network metrics are converted to MB."""
        metrics = system_monitor.get_system_metrics()

        # 100 MB sent
        sent_mb = metrics["network"]["bytes_sent"] / (1024**2)
        assert sent_mb == 100.0

        # 200 MB received
        recv_mb = metrics["network"]["bytes_recv"] / (1024**2)
        assert recv_mb == 200.0

    def test_get_system_metrics_high_cpu(self, system_monitor):
        """Test handling high CPU usage."""
        with patch("psutil.cpu_percent") as mock_cpu, patch(
            "psutil.virtual_memory"
        ) as mock_mem, patch("psutil.disk_usage") as mock_disk, patch(
            "psutil.disk_partitions"
        ) as mock_partitions, patch("psutil.net_io_counters") as mock_net:
            mock_cpu.return_value = 95.8

            mock_mem.return_value = MagicMock(percent=50.0)
            mock_mem.return_value._asdict.return_value = {"percent": 50.0}

            mock_partitions.return_value = []

            mock_net.return_value = MagicMock(bytes_sent=0, bytes_recv=0)
            mock_net.return_value._asdict.return_value = {
                "bytes_sent": 0,
                "bytes_recv": 0,
            }

            metrics = system_monitor.get_system_metrics()
            assert metrics["cpu_percent"] == 95.8

    def test_get_system_metrics_high_memory(self, system_monitor):
        """Test handling high memory usage."""
        with patch("psutil.cpu_percent") as mock_cpu, patch(
            "psutil.virtual_memory"
        ) as mock_mem, patch("psutil.disk_usage") as mock_disk, patch(
            "psutil.disk_partitions"
        ) as mock_partitions, patch("psutil.net_io_counters") as mock_net:
            mock_cpu.return_value = 50.0

            mock_mem.return_value = MagicMock(
                total=16 * 1024**3,
                available=1 * 1024**3,
                used=15 * 1024**3,
                percent=93.75,
            )
            mock_mem.return_value._asdict.return_value = {
                "total": 16 * 1024**3,
                "available": 1 * 1024**3,
                "used": 15 * 1024**3,
                "percent": 93.75,
            }

            mock_partitions.return_value = []

            mock_net.return_value = MagicMock(bytes_sent=0, bytes_recv=0)
            mock_net.return_value._asdict.return_value = {
                "bytes_sent": 0,
                "bytes_recv": 0,
            }

            metrics = system_monitor.get_system_metrics()
            assert metrics["memory"]["percent"] == 93.75

    def test_get_system_metrics_zero_values(self, system_monitor):
        """Test handling zero values in metrics."""
        with patch("psutil.cpu_percent") as mock_cpu, patch(
            "psutil.virtual_memory"
        ) as mock_mem, patch("psutil.disk_usage") as mock_disk, patch(
            "psutil.disk_partitions"
        ) as mock_partitions, patch("psutil.net_io_counters") as mock_net:
            mock_cpu.return_value = 0.0

            mock_mem.return_value = MagicMock(
                total=16 * 1024**3,
                available=16 * 1024**3,
                used=0,
                percent=0.0,
            )
            mock_mem.return_value._asdict.return_value = {
                "total": 16 * 1024**3,
                "available": 16 * 1024**3,
                "used": 0,
                "percent": 0.0,
            }

            mock_partitions.return_value = []

            mock_net.return_value = MagicMock(bytes_sent=0, bytes_recv=0)
            mock_net.return_value._asdict.return_value = {
                "bytes_sent": 0,
                "bytes_recv": 0,
            }

            metrics = system_monitor.get_system_metrics()
            assert metrics["cpu_percent"] == 0.0
            assert metrics["memory"]["percent"] == 0.0
            assert metrics["network"]["bytes_sent"] == 0
            assert metrics["network"]["bytes_recv"] == 0
