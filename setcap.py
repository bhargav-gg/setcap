#!/usr/bin/python3
import os
import sys
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser("setcap")
    parser.add_argument("add", help="This is a test")

    if os.geteuid() != 0:
        print("ERROR: This script must be run with root/sudoer privileges!")
        sys.exit()
    
    print(sys.argv)