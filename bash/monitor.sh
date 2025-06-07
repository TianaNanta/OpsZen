#!/bin/bash
THRESHOLD=80
# Check CPU load
CPU_LOAD=$(top -bn1 | grep "Cpu(s)" | awk '{print $2 + $4}')

echo "CPU Load: $CPU_LOAD%"
# Check memory usage
MEMORY=$(free | awk '/Mem:/ {printf "%.2f", $3/$2 * 100.0}')

echo "Memory Usage: $MEMORY%"
# Check disk space
DISK=$(df -h | awk '$NF=="/"{print $(NF-1)}' | sed 's/%//')

echo "Disk Usage: $DISK%"
# Alert if any metric exceeds threshold
if [[ "$CPU_LOAD" > "$THRESHOLD" || "$MEMORY" > "$THRESHOLD" || "$DISK" > "$THRESHOLD" ]]; then
echo "Alert: One of the metrics is above $THRESHOLD%"
fi
