#!/usr/bin/python3
import os
import commands
import sys
import pwd
import grp
import argparse
import configparser

if __name__ == "__main__":
    #Exit if user is not root/sudoer
    if os.geteuid() != 0:
        print("ERROR: This script must be run with sudo/root privileges!")
        sys.exit()
    
    #Existence check for configuration file--if not exists, create empty one in /etc directory
    if not os.path.isfile("/etc/setcap.ini"):
        config = configparser.ConfigParser()

        config['RAMLimits'] = {}
        config['DiskLimits'] = {}
        config['CPULimits'] = {}

        with open("/etc/setcap.ini", "w") as config_file:
            print(config)
            config.write(config_file)

    parser = argparse.ArgumentParser(prog="setcap", description="Sets resource limits by user (UID) for CPU/RAM/SSD", epilog="setcap is a Clemson University CPSC student project, the source code can be found at: https://github.com/bhargav-gg/setcap")

    """
    mode = parser.add_argument_group('mode')
    mode.add_argument("-a", "--add", action="store_true", required=False, default=False, help="Adds and/or modifies resource limits for a given user")
    mode.add_argument('-d', "--delete", action="store_true", required=False, default=False, help="Deletes resource limits for a given user")
    mode.add_argument('-v', "--view", action="store_true", required=False, default=False, help="View the current configuration file")
    mode.add_argument('-e', "--edit", action="store_true", required=False, default=False, help="Opens the configuration file for manual editing by program user")
    mode.add_argument('-i', "--install", action="store_true", required=False, default=False, help="Installs the current configuration file into the respective cgroups/quota files")
    mode.add_argument('-c', "--current", action="store_true", required=False, default=False, help="View snapshot of all users' RAM/CPU/Storage")

    parser.add_argument('user', action='store', type=str, help='User whose limits are being added/modified/removed')

    parser.add_argument('ram', action='store', type=str, help='RAM limits, supports KB/MB/GB/raw integer', required=False)
    """

    parser.add_argument('mode', action='store', type=str, choices=['addmod', 'delete', 'view', 'edit', 'install', 'current'], help='Mode of operation')
    parser.add_argument('-u', '--user', action='store', type=str, help='User whose limits are being added/modified/removed')
    parser.add_argument('-m', '--memory', action='store', type=str, help='Memory limits, supports KB/MB/GB/raw integer', required=False)
    parser.add_argument('-c', '--cpu', action='store', type=str, help='CPU limits, supports percentage', required=False)
    parser.add_argument('-s', '--storage', action='store', type=str, help='Storage limits, supports KB/MB/GB/raw integer', required=False)

    args = vars(parser.parse_args())
    print(args)

    #NEEDS USER
    if args['mode'] == 'addmod':
        print("Adding/Modifying...")
        commands.addmod()
    #NEEDS USER
    elif args['mode'] == 'delete':
        print("Deleting...")
    elif args['mode'] == 'view':
        print("Viewing...")
    elif args['mode'] == 'edit':
        print('Editing...')
    elif args['mode'] == 'install':
        print("Installing...")
    elif args['mode'] == 'current':
        print('Showing current snapshot...')

    