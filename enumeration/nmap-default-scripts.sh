#!/usr/share/env bash

if [ $UID -ne 0 ]; then
    echo "[-] This script must be ran as root"
    exit 1
fi

target="$1"
file_name="$2"
nmap_directory="$(pwd)/nmap"

[ -z "$target" ] && { echo "Usage: $0 <target> <file_name>"; exit 1; }
[ -d "$nmap_directory" ] || { echo "[-] nmap directory not found: $nmap_directory"; exit 1; }

if ! [[ "$target" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "[-] Invalid target IP address: $target"
    exit 1
fi

nmap "$target" -sSCV -vv -oA "${nmap_directory}/${file_name}"