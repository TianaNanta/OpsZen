#!/bin/bash
echo "===== Basic Security Audit ====="

# 1. Check firewall status
echo -e "\n** Firewall Status **"
sudo ufw status || sudo iptables -L

# 2. Check SSH configuration (PermitRootLogin and PasswordAuthentication)
echo -e "\n** SSH Configuration Check **"
grep -E "^PermitRootLogin|^PasswordAuthentication" /etc/ssh/sshd_config

# 3. Check for available package updates
echo -e "\n** Package Update Check **"
Sudo apt update && apt list - upgradable

# 4. Check for open listening ports
echo -e "\n** Open Ports **"
ss -tuln
# 5. Check user accounts with superuser privileges
echo -e "\n** Users with Superuser Privileges **"
getent group sudo

echo "===== Security Audit Complete ====="
