import os
import sys
import wget
import pwd
import json
from colorama import Fore, init

# Initialize colorama
init(autoreset=True)

# Get current user
sysuser = str(pwd.getpwuid(os.getuid())[0])

# Define paths
base_path = f"/home/{sysuser}/npac"
SysTake = os.path.join(base_path, "downloads/")
appdir = os.path.join(base_path, "applications/")
pldir = os.path.join(base_path, "PL/")
typedirs = {
    ".deb": os.path.join(base_path, "deb/"),
}

# Ensure directories exist
os.makedirs(SysTake, exist_ok=True)
os.makedirs(appdir, exist_ok=True)
os.makedirs(pldir, exist_ok=True)
for path in typedirs.values():
    os.makedirs(path, exist_ok=True)

# Print install locations
print(Fore.RED + "Applications will be installed to: " + Fore.WHITE + appdir)
print(Fore.RED + "Downloaded files via 'npac steal' will be stored at: " + Fore.WHITE + SysTake)
print(Fore.RED + "Package Lists directory: " + Fore.WHITE + pldir)
print()

# Show help message
def show_help():
    print(Fore.CYAN + """
npac - A Python-based Linux package manager

Usage:
  npac get <package> [-f]        Install a package (force install with -f)
  npac delete <package> [-f]     Remove a package (force remove with -f)
  npac patch <package|all> [-f]  Update a package or all packages
  npac steal <url>               Download a file from the internet
  npac refresh <letter|all>      Refresh package list(s)
  npac help                      Show this help message
""")

# Download a package file
def download_package(url):
    ext = ".deb"  # Now, only handle .deb files
    outdir = typedirs.get(ext)
    
    try:
        print(Fore.GREEN + f"Downloading {url} to {outdir}")
        filename = wget.download(url, out=outdir)
        print(Fore.GREEN + f"\nSaved as: {filename}")
    except Exception as e:
        print(Fore.RED + f"Download failed: {e}")

# Search JSON file based on first letter of package name
def find_package(pac_name):
    pac_name_lower = pac_name.lower()
    first_letter = pac_name_lower[0]
    json_file = os.path.join(pldir, f"{first_letter}.json")

    if not os.path.exists(json_file):
        print(Fore.RED + f"Package list '{first_letter}.json' not found. Try running: npac refresh {first_letter}")
        return None

    try:
        with open(json_file, "r") as f:
            data = json.load(f)
            package = data.get(pac_name_lower)
            if not package:
                print(Fore.RED + f"Package '{pac_name}' not found in {json_file}.")
                return None
            return package
    except json.JSONDecodeError as e:
        print(Fore.RED + f"Failed to read or parse {json_file}: {e}")
        return None

# Install a package
def install(pacName, version=None, force=False):
    print(Fore.YELLOW + f"Looking for {pacName}...")
    entry = find_package(pacName)
    if not entry:
        print(Fore.RED + f"Package '{pacName}' not found in local package lists.")
        return
    url = entry.get("url")
    if not url:
        print(Fore.RED + f"No URL found for {pacName}")
        return
    print(Fore.YELLOW + f"Found {pacName}, downloading...")
    download_package(url)

# Refresh a package list
def refresh(letter):
    urls = []
    if letter == "all":
        # If 'all' is specified, we download all letters from 'a' to 'z'
        urls = [f"https://github.com/DiscoKnax6808/npacpackagelists/raw/refs/heads/main/{chr(i)}.json" for i in range(97, 123)]
    else:
        letter = letter.lower()
        if len(letter) == 1 and 'a' <= letter <= 'z':
            # If a specific letter is specified, download only that letter's list
            urls = [f"https://github.com/DiscoKnax6808/npacpackagelists/raw/refs/heads/main/{letter}.json"]
        else:
            print(Fore.RED + "Invalid letter for refresh.")
            return

    # Remove only the old .json files corresponding to the requested letter or all
    if letter == "all":
        # If 'all' is specified, delete all .json files
        for file in os.listdir(pldir):
            if file.endswith(".json"):
                print(Fore.YELLOW + f"Deleting old package list {file} to avoid stacking...")
                os.remove(os.path.join(pldir, file))
    else:
        # If a specific letter is specified, delete only that letter's .json file
        json_file = f"{letter}.json"
        json_file_path = os.path.join(pldir, json_file)
        if os.path.exists(json_file_path):
            print(Fore.YELLOW + f"Deleting old package list {json_file} to avoid stacking...")
            os.remove(json_file_path)

    # Now download the updated package list(s)
    for url in urls:
        filename = url.split("/")[-1]
        path = os.path.join(pldir, filename)

        try:
            print(Fore.YELLOW + f"Fetching {url}")
            wget.download(url, out=path)
            print(Fore.GREEN + f"\nSaved to {path}")
        except Exception as e:
            print(Fore.RED + f"Failed to download {url}: {e}")


def update(pacName=None, force=False):
    if pacName == "all":
        print(Fore.YELLOW + "Patching all packages" + (" with force." if force else "."))
    else:
        print(Fore.YELLOW + f"Patching {pacName}" + (" with force." if force else "."))

def remove(pacName, force=False):
    print(Fore.YELLOW + f"Deleting {pacName}" + (" with force." if force else "."))

def take(url):
    try:
        print(Fore.GREEN + f"Downloading from: {url}")
        filename = wget.download(url, out=SysTake)
        print(Fore.GREEN + f"\nDownloaded as: {filename}")
    except Exception as e:
        print(Fore.RED + f"Download failed: {e}")

# Main CLI Handler
def main():
    if len(sys.argv) < 2:
        show_help()
        return

    command = sys.argv[1]
    args = sys.argv[2:]

    if command == "get":
        if len(args) == 0:
            print(Fore.RED + "Usage: npac get <package> [-f]")
            return
        pac = args[0]
        force = "-f" in args
        install(pac, force=force)

    elif command == "patch":
        if len(args) == 0:
            print(Fore.RED + "Usage: npac patch <package|all> [-f]")
            return
        pac = args[0]
        force = "-f" in args
        update(pac, force=force)

    elif command == "delete":
        if len(args) == 0:
            print(Fore.RED + "Usage: npac delete <package> [-f]")
            return
        pac = args[0]
        force = "-f" in args
        remove(pac, force=force)

    elif command == "steal":
        if len(args) != 1:
            print(Fore.RED + "Usage: npac steal <url>")
            return
        url = args[0]
        take(url)

    elif command == "refresh":
        if len(args) != 1:
            print(Fore.RED + "Usage: npac refresh <letter|all>")
            return
        refresh(args[0])

    elif command == "help":
        show_help()

    else:
        print(Fore.RED + f"Unknown command: {command}")
        show_help()

if __name__ == "__main__":
    main()
