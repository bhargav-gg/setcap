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
The installation process, with the OS specification in the `Support` section, assumes that the user has the `apt` package manager used by Ubuntu.
While cgroups are integrated as a feature within the Linux kernel itself, `quota` (despite being a UNIX standard with accompanying man pages) may not be installed by default on your Ubuntu system. It can be installed with:
```
sudo apt install quota
```
After you have installed `quota`, it is important to go to `/etc/fstab`, find the line that describes your main Linux partition (for the sake of concept simplicity, setcap as of now only works with one partition), usually having ext4, and replace the `defaults` option with `usrquota`. After doing that, the user should remount their file system so that it follows these new options: `sudo mount -o remount /` (assuming your partition is mounted at /). The user can then create the corresponding limit info files using the command: `sudo quotacheck -ugm -F vfsv1 /`. Lastly, because of the modular nature of the Linux kernel, it is important to load the module into the kernel itself. First, identify the versions of `quota_v1` and `quota_v2` using the following command: `find /lib/modules/ -type f -name '*quota_v*.ko*'`. In this case, we are mainly interested in the version (the section after `/lib/modules`). After identifying your versions, add the modules to the kernel using the following commands: `sudo modprobe quota_v1 -S <kernel_version>` and `sudo modprobe quota_v2 -S <kernel_version>`. Lastly, activate the quota system with the `sudo quotaon -v /` command. That is all the setup necessary, `setcap` serves as an interface between the user and any necessary modifications to this quota system.
setcap also relies on `cgroup-tools`, particular the `cgrulesengd`, to automatically assign processes by a certain user to the appropriate control group. It uses the configuration file located at `/etc/cgconfig.d` and can be installed using:
```
sudo apt install cgroup-tools
```
`setcap` will manage the rest of the cgroups process for you, including the usage of `cgrulesengd`.
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

The makefile (`Makefile`) comes with several targets used to facilitate testing and installation of the program:
- `compile`: Using pyinstaller, compiles the `setcap.py` into a binary executable that is moved to `/sbin/setcap` so that it can be used anywhere by the system administrator

## Usage
The usage of this program is detailed by running the program with the '-h' flag