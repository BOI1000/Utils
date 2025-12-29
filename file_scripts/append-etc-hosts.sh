#!/usr/bin/env bash
if [ $UID -ne 0 ]; then
    echo "[-] This script must be run as root"
    exit 1
fi

hosts_file="/etc/hosts"
entry="$1"
hostnames="${@:2}"

if [ -z "$entry" ] || [ -z "$hostnames" ]; then
    echo "Usage: $0 <IP_ADDRESS> <HOSTNAME1> [HOSTNAME2 ... HOSTNAMEx"
    exit 1
fi

if ! [[ "$entry" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "[-] Invalid IP address: $entry"
    echo "Usage: $0 <IP_ADDRESS> <HOSTNAME1> [HOSTNAME2 ... HOSTNAMEx]"
    exit 1
fi

for hostname in $hostnames; do
    if grep -qE "^\s*$entry\s+$hostname(\s|$)" "$hosts_file"; then
        echo "[*] Entry for $hostname, IP: $entry already exists in $hosts_file"
    else
        echo "[*] Adding entry: $entry : $hostname to $hosts_file"
        echo -e "$entry\t$hostname" >> "$hosts_file"
    fi
done

echo "[*] Completed updating $hosts_file"