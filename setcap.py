#!/usr/bin/python3
##############################################
# Driver file, used to set up command line interface and pass arguments to the commands module, which performs the actual commands
##############################################
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
    
    #Create command line argument parser with appropriate options
    parser = argparse.ArgumentParser(prog="setcap", description="Sets resource limits by user (UID) for CPU/RAM/SSD", epilog="setcap is a Clemson University CPSC student project, the source code can be found at: https://github.com/bhargav-gg/setcap")

    parser.add_argument('mode', action='store', type=str, choices=['addmod', 'delete', 'view', 'editor', 'install'], help='Mode of operation')
    parser.add_argument('-u', '--user', action='store', type=str, help='User whose limits are being added/modified/removed (addmod/delete)')
    parser.add_argument('-m', '--memory', action='store', type=str, help='Memory limits, supports KB/MB/GB/raw integer (addmod)', required=False)
    parser.add_argument('-c', '--cpu', action='store', type=str, help='CPU limits, supports percentage (addmod)', required=False)
    parser.add_argument('-s', '--storage', action='store', type=str, help='Storage limits, supports KB/MB/GB/raw integer (addmod)', required=False)
    parser.add_argument('-a', '--application', action='store', type=str, help="New editor application to use to quick open configuration file (editor)")

    #Gets parsed arguments
    args = vars(parser.parse_args())

    #addmod needs -u [user] argument and at least one resource limit (-c, -m, -s)
    if args['mode'] == 'addmod':
        #Stop if no user argument provided
        if not args['user']:
            print("ERROR: No username was provided!")
            sys.exit()
        
        #Convert user -> UID
        uid = caputils.uid_from_name(args['user'])

        #Stop if conversion failed (no such UID, thus user, exists)
        if not uid:
            print("ERROR: Username was provided, but was not able to be resolved into a UID!")
            sys.exit()
        
        #Stop if trying to set limits on root
        if uid == 0:
            print("ERROR: Cannot set limits on root user!")
            sys.exit()
        
        #Stop if no resource limited
        if not args['memory'] and not args['cpu'] and not args['storage']:
            print("ERROR: addmod needs at least one limit, i.e. memory (-m, --memory), CPU (-c, --cpu), storage (-s, --storage)")
            sys.exit()
        
        #If memory limit is supplied, convert limit to raw bytes
        if args['memory']:
            args['memory'] = caputils.stringbytes_to_integer(args['memory'], "RAM")

            if args['memory'] is None:
                sys.exit()
        
        #If CPU max % usage is supplied, convert to raw integer
        if args['cpu']:
            args['cpu'] = re.sub("\\%", "", args['cpu'])

            try:
                args['cpu'] = int(args['cpu'])
            except:
                print("ERROR: Cannot cast CPU limit into integer!")
                sys.exit()
        
        #If storage limit is supplied, convert limit to raw bytes
        if args['storage']:
            args['storage'] = caputils.stringbytes_to_integer(args['storage'], "storage")

            if args['storage'] is None:
                sys.exit()

        #Send cleaned arguments to commands module to perform addmod
        commands.addmod(uid=str(uid), cpu=args['cpu'], ram=args['memory'], storage=args['storage'])
    #delete needs -u [user] argument
    elif args['mode'] == 'delete':
        #Stop if no username provided
        if not args['user']:
            print("ERROR: No username was provided!")
            sys.exit()
        
        #Converts username -> UID
        uid = caputils.uid_from_name(args['user'])

        #Stop if conversion failed
        if not uid:
            print("ERROR: Username was provided, but was not able to be resolved into a UID!")
            sys.exit()
        
        #Send cleaned argument to commands module to perform delete
        commands.delete(str(uid))
    #Perform view--no arguments/cleaning needed
    elif args['mode'] == 'view':
        commands.view()
    #Perform editor--no cleaning (trusts user to pick valid editor command if supplied)
    elif args['mode'] == 'editor':
        commands.editor(args['application'])
    #Perform install--no arguments/cleaning needed
    elif args['mode'] == 'install':
        commands.install()

    