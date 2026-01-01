#!/usr/bin/env python3
import argparse
import os
import re
import ipaddress

def append_to_hosts_file(ip_address, hostnames, hosts_file="/etc/hosts"):
    """Append hostnames to the given IP in `hosts_file`.

    If the IP already exists in the file, merge hostnames (no duplicates) and preserve
    the first inline comment found. Returns the final line written (including newline).
    """
    # Validate IPv4 address using stdlib
    try:
        ip_obj = ipaddress.ip_address(ip_address)
    except ValueError:
        raise ValueError("[-] Invalid IP address format.")
    if ip_obj.version != 4:
        raise ValueError("[-] Only IPv4 addresses are supported.")

    if not hostnames:
        raise ValueError("[-] No hostnames provided to append.")

    updated_lines = []
    found = False
    collected_hostnames = []
    preserved_comment = None

    # Read current file and collect hostnames for this IP (skip original IP lines)
    try:
        with open(hosts_file, "r") as f:
            for line in f:
                parts = line.split("#", 1)
                mapping = parts[0].strip()
                comment = "#" + parts[1] if len(parts) > 1 else ""
                
                if re.match(r'^\s*' + re.escape(ip_address) + r'(\s+|$)', mapping):
                    found = True
                    tokens = mapping.split()
                    collected_hostnames.extend(tokens[1:])
                    if not preserved_comment and comment:
                        preserved_comment = comment
                    # skip original line; we'll replace with merged one
                else:
                    updated_lines.append(line)
    
    except FileNotFoundError:
        # If the hosts file doesn't exist, treat as empty
        updated_lines = []

    def _dedupe_preserve_order(seq):
        seen = set()
        out = []
        for x in seq:
            if x not in seen:
                seen.add(x)
                out.append(x)
        return out

    if found:
        final_hostnames = _dedupe_preserve_order(collected_hostnames + hostnames)
        new_line = ip_address + " " + " ".join(final_hostnames) + (" " + preserved_comment if preserved_comment else "") + "\n"
        updated_lines.append(new_line)
        with open(hosts_file, "w") as f:
            f.writelines(updated_lines)
        return new_line

    # If not found, append a conventional entry (ip\t host1 host2...)
    entry = f"{ip_address} " + "\t" + " ".join(hostnames) + "\n"
    with open(hosts_file, "a") as f:
        f.write(entry)

    return entry

def remove_host_from_entry(ip_address, hostname, hosts_file="/etc/hosts"):
    """Remove a specific hostname from the entry for the provided IPv4 address in /etc/hosts.
    Returns True if the hostname was removed, False if not found.
    """
    
    if not re.match(r"^\d{1,3}(\.\d{1,3}){3}$", ip_address,):
        raise ValueError("[-] Invalid IP address format.")

    modified = False
    updated_lines = []

    with open(hosts_file, "r") as f:
        for line in f:
            # Separate any inline comment so we only match the actual mapping portion
            parts = line.split("#", 1)
            mapping = parts[0].strip()
            comment = "#" + parts[1] if len(parts) > 1 else ""

            if re.match(r'^\s*' + re.escape(ip_address) + r'(\s+|$)', mapping):
                # Split the mapping into IP and hostnames
                tokens = mapping.split()
                ip = tokens[0]
                hostnames_list = tokens[1:]

                if hostname in hostnames_list:
                    hostnames_list.remove(hostname)
                    modified = True

                if hostnames_list:
                    new_mapping = ip + " " + " ".join(hostnames_list)
                    updated_lines.append(new_mapping + " " + comment + "\n")
                else:
                    # If no hostnames left, skip this line (effectively removing it)
                    continue
            else:
                updated_lines.append(line)

    if modified:
        with open(hosts_file, "w") as f:
            f.writelines(updated_lines)

    return modified

# TODO: patch vauge message when the following commands are executed:
    # ./etc_hosts_manage.py 10.10.10.10 example.com
    # ./etc_hosts_manage.py 10.10.10.10 --remove-hostname example.com
    # ./etc_hosts_manage.py 10.10.10.10 --remove
    # some output: [-] No entries found for 10.10.10.10

def remove_entry_from_hosts_file(ip_address, hosts_file="/etc/hosts"):
    """Remove any lines from /etc/hosts that belong to the provided IPv4 address.
    Returns a list of removed lines (including their trailing newlines), or None if nothing removed.
    """
    
    if not re.match(r"^\d{1,3}(\.\d{1,3}){3}$", ip_address):
        raise ValueError("[-] Invalid IP address format.")
    
    removed_lines = []
    kept_lines = []

    with open(hosts_file, "r") as f:
        for line in f:
            # Separate any inline comment so we only match the actual mapping portion
            mapping = line.split("#", 1)[0].strip()
            # Match when the mapping is exactly the IP, or IP followed by whitespace and hostnames
            if mapping == ip_address or mapping.startswith(ip_address + " ") or mapping.startswith(ip_address + "\t"):
                removed_lines.append(line)
            else:
                kept_lines.append(line)

    if not removed_lines:
        return None

    with open(hosts_file, "w") as f:
        f.writelines(kept_lines)

    return removed_lines

def get_entries_from_hosts_file(ip_address, hosts_file="/etc/hosts"):
    """Retrieve all lines from /etc/hosts that belong to the provided IPv4 address.
    Returns a list of matching lines (including their trailing newlines), or None if nothing found.
    """
    if not re.match(r"^\d{1,3}(\.\d{1,3}){3}$", ip_address):
        raise ValueError("[-] Invalid IP address format.")
    
    matching_lines = []

    with open(hosts_file, "r") as f:
        for line in f:
            # Separate any inline comment so we only match the actual mapping portion
            mapping = line.split("#", 1)[0].strip()
            # Match when mapping is exactly the IP, or IP followed by whitespace and hostnames
            if mapping == ip_address or mapping.startswith(ip_address + " ") or mapping.startswith(ip_address + "\t"):
                matching_lines.append(line)

    return matching_lines if matching_lines else None

def request_root():
    import sys
    if hasattr(os, 'geteuid') and os.geteuid() != 0:
        args = ["sudo", sys.executable] + sys.argv + [os.environ]
        os.execlpe("sudo", *args)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage entries in the /etc/hosts file.")
    parser.add_argument("ip_address", help="IP address to associate with hostname(s).")
    parser.add_argument("hostnames", nargs="*", help="One or more hostnames to associate with the IP address.")
    parser.add_argument("-r", "--remove", action="store_true", help="Remove the entry for the given IP address (removes the entire line).")
    parser.add_argument("-rh", "--remove-hostname", metavar="HOSTNAME", help="Remove a specific hostname from the entry for the given IP address.")
    parser.add_argument("--hosts-file", default="/etc/hosts", help="Path to the hosts file (default: /etc/hosts).")
    parser.add_argument("--get-entry", action="store_true", help="Get the entry for the given IP address.")
    parser.add_argument("--backup", action="store_true", help="Create a backup of the hosts file before making changes.")
    args = parser.parse_args()

    if args.hosts_file == "/etc/hosts":
        request_root()

    if args.backup:
        backup_path = args.hosts_file + ".bak"
        with open(args.hosts_file, "r") as original, open(backup_path, "w") as backup:
            backup.writelines(original.readlines())
        
        print(f"[*] Backup of hosts file created at: {backup_path}")

    print(f"[*] Using hosts file: {args.hosts_file}")
    if args.remove:
        if args.hostnames:
            parser.error("the --remove option cannot be used with hostnames")

        removed = remove_entry_from_hosts_file(args.ip_address, args.hosts_file)
        if removed:
            print(f"[*] Removed {len(removed)} line(s):")
            for l in removed:
                print(l, end="")
        else:
            print(f"[-] No entries found for {args.ip_address}")
    
    elif args.remove_hostname:
        success = remove_host_from_entry(args.ip_address, args.remove_hostname, args.hosts_file)
        if success:
            entry = get_entries_from_hosts_file(args.ip_address, args.hosts_file)
            print(f"[*] Removed hostname '{args.remove_hostname}' from {args.ip_address}")
            if entry:
                for l in entry:
                    print(l, end="")
        
        else:
            print(f"[-] Hostname '{args.remove_hostname}' not found for {args.ip_address}")
    
    elif args.get_entry:
        entry = get_entries_from_hosts_file(args.ip_address, args.hosts_file)
        if entry:
            print(f"[*] Found {len(entry)} line(s) for {args.ip_address}:")
            for l in entry:
                print(l, end="")
        else:
            print(f"[-] No entries found for {args.ip_address}")
    
    else:
        if not args.hostnames:
            parser.error("the following arguments are required: hostnames (unless --remove is used)")
        
        output = append_to_hosts_file(args.ip_address, args.hostnames, args.hosts_file)
        print(f"{output.strip()}")
