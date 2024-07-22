# setcap

## Description
setcap is a small, lightweight way for system administrators to impose specific resource limits on each of their users. setcap, in particular, serves as a simple frontend for Linux cgroups V2 (RAM, CPU) and quota (storage). It essentially bundles features of both of these separate applications to provide a complete system restriction suite on a user-by-user basis.

## Support
This program has been developed and tested on the Ubuntu 22.04.4 LTS (Jammy Jellyfish) operating system. The author cannot guarantee its functionality on any other Ubuntu distribution version, any other Linux distribution entirely, or any other operating system, i.e. Windows or macOS.

The author of this program can be reached at bhargap@clemson.edu (or bhargav@bhargav.gg). The source code of this program can be found at https://github.com/bhargav-gg/setcap. Using the setcap executable (or Python file, whichever the reader prefers) list the possible options/subcommands available to the user through this program. Lastly, documentation for cgroups and quota, for the developer, can be found using the following respective commands:
```
man cgroups
man quota
```

## Installation
While cgroups are integrated as a feature within the Linux kernel itself, `quota` (despite being a UNIX standard with accompanying man pages) may not be installed by default on your Ubuntu system. It can be installed with:
```
sudo apt install quota
```
Python is the programming language of choice for this application and can be installed similarly with:
```
sudo apt install python3
```
Lastly and optionally, the setcap program can be made into a compiled executable binary using pyinstaller, if the user prefers. This can be installed with:
```
sudo apt install pip
pip install pyinstaller --break-system-packages
```
The `--break-system-packages` flag is used because Ubuntu is a package-managed OS distribution, which may be in conflict with pip. Alternatively, if the user is comfortable, they could set up a Python virtual environment (venv) for their pip packages, but that will not be discussed here and the user is encouraged to look that up on their own (and contribute instructions to this README if desiring).

## Usage