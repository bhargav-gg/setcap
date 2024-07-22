#!/usr/bin/python3
import os
import sys
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
    parser.add_argument("-a", "--add", action="store_true")
    parser.add_argument('-d', "--delete", action="store_true")
    parser.add_argument('-r', "--remove", action="store_true")
    parser.add_argument('-v', "--view", action="store_true")
    args = vars(parser.parse_args())

    #implicit -h/--help if no arguments are given
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit()

    print(args)