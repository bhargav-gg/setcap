#!/usr/bin/python3
import os
import re
import commands
import caputils
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
        caputils.create_empty_config("/etc/setcap.ini")

    parser = argparse.ArgumentParser(prog="setcap", description="Sets resource limits by user (UID) for CPU/RAM/SSD", epilog="setcap is a Clemson University CPSC student project, the source code can be found at: https://github.com/bhargav-gg/setcap")

    parser.add_argument('mode', action='store', type=str, choices=['addmod', 'delete', 'view', 'edit', 'install'], help='Mode of operation')
    parser.add_argument('-u', '--user', action='store', type=str, help='User whose limits are being added/modified/removed')
    parser.add_argument('-m', '--memory', action='store', type=str, help='Memory limits, supports KB/MB/GB/raw integer', required=False)
    parser.add_argument('-c', '--cpu', action='store', type=str, help='CPU limits, supports percentage', required=False)
    parser.add_argument('-s', '--storage', action='store', type=str, help='Storage limits, supports KB/MB/GB/raw integer', required=False)

    args = vars(parser.parse_args())

    #NEEDS USER
    if args['mode'] == 'addmod':
        if not args['user']:
            print("ERROR: No username was provided!")
            sys.exit()
        
        uid = caputils.uid_from_name(args['user'])

        if not uid:
            print("ERROR: Username was provided, but was not able to be resolved into a UID!")
            sys.exit()
        
        if not args['memory'] and not args['cpu'] and not args['storage']:
            print("ERROR: addmod needs at least one limit, i.e. memory (-m, --memory), CPU (-c, --cpu), storage (-s, --storage)")
            sys.exit()

        if args['memory']:
            args['memory'] = caputils.stringbytes_to_integer(args['memory'], "RAM")

            if args['memory'] is None:
                sys.exit()

        if args['cpu']:
            args['cpu'] = re.sub("\%", "", args['cpu'])

            try:
                args['cpu'] = int(args['cpu'])
            except:
                print("ERROR: Cannot cast CPU limit into integer!")
                sys.exit()
        
        if args['storage']:
            args['storage'] = caputils.stringbytes_to_integer(args['storage'], "storage")

            if args['storage'] is None:
                sys.exit()

        
        commands.addmod(uid=str(uid), cpu=args['cpu'], ram=args['memory'], storage=['storage'])
    #NEEDS USER
    elif args['mode'] == 'delete':
        if not args['user']:
            print("ERROR: No username was provided!")
            sys.exit()
        
        uid = caputils.uid_from_name(args['user'])

        if not uid:
            print("ERROR: Username was provided, but was not able to be resolved into a UID!")
            sys.exit()
        
        commands.delete(uid)
    elif args['mode'] == 'view':
        commands.view()
    elif args['mode'] == 'edit':
        commands.edit()
    elif args['mode'] == 'install':
        commands.install()

    