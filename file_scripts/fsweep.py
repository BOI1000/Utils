#!/usr/bin/env python3
import os
import shutil
import argparse

def fsweep(directory):
    if not os.path.isdir(directory):
        print("[-] The specified path is not a directory.")
        return
    
    if os.path.abspath(directory) == os.path.abspath(os.getcwd()):
        print("[-] The specified directory is the current working directory.\n",
        "[?] Are you sure you want to proceed? [y/N]: ", end="")
        choice = input().strip().lower()
        if choice not in ('y', 'Y', 'yes'):
            print("[*] Operation cancelled")
            return

    try:
        current_dir = os.getcwd()

        # exclude all directories
        with os.scandir(current_dir) as dir_contents:
            for file in dir_contents:
                if file.is_file():
                    shutil.move(file.path, os.path.join(directory, file.name))
                    print(f"[+] {file.name} → {os.path.join(directory, file.name)}")

        return

    except PermissionError:
        print("[-] Permission denied to access the directory.")
        return

    except FileNotFoundError:
        print("[-] The specified directory does not exist.")
        return

    except Exception as e:
        print(f"[-] An error occurred: {e}")
        return

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="File sweeper: Move all files from the current directory to a specified directory. (does not include directories)")
    parser.add_argument("directory", help="Directory to move files into.")

    args = parser.parse_args()
    fsweep(args.directory)

