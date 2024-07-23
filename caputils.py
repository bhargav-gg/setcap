import os
import sys
import pwd
import re
import grp
import configparser

def get_size(start = '.'):
    size = 0

    for dirpath, dirnames, filenames in os.walk(start):
        for f in filenames:
            fp = os.path.join(dirpath, f)

            if not os.path.islink(fp):
                size += os.path.getsize(fp)
    
    return size

def uid_from_name(name: str):
    try:
        uid = pwd.getpwnam(name).pw_uid
        return uid
    except:
        return None

def name_from_uid(uid: int):
    try:
        name = pwd.getpwuid(uid).pw_name
        return name
    except Exception as e:
        print(str(e))
        return None

def stringbytes_to_integer(stringbytes: str, resource: str):
    mult: int = 1
    stringbytes = str.lower(stringbytes)

    if re.match(".*kb", stringbytes):
        mult = 1_024
    elif re.match(".*mb", stringbytes):
        mult = 1_024 * 1024
    elif re.match(".*gb", stringbytes):
        mult = 1_024 * 1_024 * 1_024
    
    stringbytes = re.sub("kb", "", stringbytes)
    stringbytes = re.sub("mb", "", stringbytes)
    stringbytes = re.sub("gb", "", stringbytes)

    try:
        stringbytes = float(stringbytes)
        stringbytes *= mult
        return stringbytes
    except:
        print(f"ERROR: Cannot cast {resource} limit into integer!")
        return None

def integer_to_stringbytes(number: float):
    if number >= (1_024 * 1_024 * 1_024):
        return f"{number / (1_024 * 1_024 * 1_024):.2f}GB"
    elif number >= (1_024 * 1_024):
        return f"{number / (1_024 * 1_024):.2f}MB"
    elif number >= 1_024:
        return f"{number / 1_024:.2f}KB"
    
    return number

def create_empty_config(path: str):
    config = configparser.ConfigParser()

    config['RAMLimits'] = {}
    config['DiskLimits'] = {}
    config['CPULimits'] = {}
    config['Editor'] = {'app': 'nano'}

    with open("/etc/setcap.ini", "w") as config_file:
        config.write(config_file)