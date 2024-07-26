##############################################
# Performs the heavy lifting--actually performing the commands specified by the user
##############################################

import configparser
import caputils
import os
import pwd
import re
import subprocess
import grp

#Adds or modifies resource limits
def addmod(uid: str, cpu: float, ram: int, storage: int):

    #Opens up configuration file and sets new limits as they are supplied
    config = configparser.ConfigParser()
    
    with open('/etc/setcap.ini', "r") as config_file:
        config.read_file(config_file)
    
    if ram and ram >= 0:
        config.set('RAMLimits', uid, str(ram))
    
    if cpu and cpu >= 0.0:
        config.set('CPULimits', uid, str(cpu))
    
    if storage and storage >= 0:
        config.set('DiskLimits', uid, str(storage))

    with open('/etc/setcap.ini', "w") as config_file:
        config.write(config_file)


#Removes resource limits
def delete(uid: str):
    #Opens up configuration file and removes previously established limits if they exist
    config = configparser.ConfigParser()

    with open('/etc/setcap.ini', "r") as config_file:
        config.read_file(config_file)
    
    if config.has_option('RAMLimits', uid):
        config.remove_option('RAMLimits', uid)
    
    if config.has_option('CPULimits', uid):
        config.remove_option('CPULimits', uid)
    
    if config.has_option('DiskLimits', uid):
        config.remove_option('DiskLimits', uid)
    
    #Removes limits from quota/cgroups in one fell swoop
    subprocess.run(["sudo", "setquota", "-u", uid, "0", "0", "0", "0", "/"])

    if os.path.isdir(f'/sys/fs/cgroup/{uid}'):
        subprocess.run(["sudo", "rmdir", f"/sys/fs/cgroup/{uid}"])
    
    if os.path.isfile(f'/etc/cgrules.conf'):
        contents = ""

        with open('/etc/cgrules.conf', "r") as file:
            contents = file.read()
        
        contents = re.sub(f"{caputils.name_from_uid(int(uid))}\\s*cpu,ram\\s*/sys/fs/cgroup/{uid}", "", contents)

        with open('/etc/cgrules.conf', "w") as file:
            file.write(contents)
    
    with open('/etc/setcap.ini', "w") as config_file:
        config.write(config_file)

#Prints resource usage + limits for all non-service users
def view():
    print(f"{"UID":<17}{"Username":<17}{"CPU Usage":<17}{"RAM Usage":<17}{"Storage Usage":<17}{"CPU Limit":<17}{"RAM Limit":<17}{"Storage Limit":<17}")
    print("-------------------------------------------------------------------------------------------------------------------------------------------")

    #Go through all processes' files and calculate total memory/CPU usage at given time
    config = configparser.ConfigParser()
    ram_dict = {}
    cpu_dict = {}

    #Grab process directory
    directory = os.fsencode("/proc")
    
    #Go through every file/directory in the /proc directory
    for file in os.listdir(directory):
        #Get the filename
        filename = os.fsdecode(file)

        #Make sure that the filename/directoryname is only numerical (indicative of process/PID)
        if re.match("\\d+", filename):
            owner = None

            #Get owner of file, skip if fails
            try:
                with open(f"/proc/{filename}/loginuid") as owner_file:
                    owner = owner_file.read()
                    owner = int(owner)

                    if(owner >= 4_000_000_000):
                        owner = 0
            except:
                continue
            
            #Defaults in case of empty dict entries/first time inserts
            if owner not in ram_dict:
                ram_dict[owner] = []
            
            if owner not in cpu_dict:
                cpu_dict[owner] = []

            #Calculate process memory usage
            ram = os.popen(f"""cat /proc/{filename}/smaps | grep -i pss |  awk '{{Total+=$2}} END {{print Total/1024/1024"GB"}}'""").read()
            ram = caputils.stringbytes_to_integer(ram, resource="RAM")

            #Get process CPU usage from ps
            cpu = os.popen(f"ps -p {filename} -o %cpu").read()
            cpu = re.sub("%CPU", "", cpu)
            cpu = cpu.strip(' \n\t')
            cpu = float(cpu)

            #Add to list in dict
            ram_dict[owner].append(ram)
            cpu_dict[owner].append(cpu)
    
    #Read configuration file to get limits
    with open('/etc/setcap.ini', "r") as config_file:
        config.read_file(config_file)
    
    #For each user in the system
    for p in pwd.getpwall():
        #If the user is a non-service user or root...
        if p.pw_uid != 65534 and p.pw_uid >= 1000 or p.pw_uid == 0:
            ram_limit = None
            cpu_limit = None
            disk_limit = None

            disk_usage = None
            cpu_usage = 0.0
            ram_usage = 0.0

            if p.pw_uid in cpu_dict:
                cpu_usage = sum(cpu_dict[p.pw_uid])
                cpu_usage = round(cpu_usage, 2)
            
            if p.pw_uid in ram_dict:
                ram_usage = sum(ram_dict[p.pw_uid])


            if p.pw_uid != 0:
                disk_usage = caputils.get_size(f"/home/{p.pw_name}")
                disk_usage = caputils.integer_to_stringbytes(disk_usage)

            if config.has_option('RAMLimits', str(p.pw_uid)):
                ram_limit = config.get('RAMLimits', str(p.pw_uid))
                ram_limit = int(float(ram_limit))
                ram_limit = caputils.integer_to_stringbytes(ram_limit)
            
            if config.has_option('CPULimits', str(p.pw_uid)):
                cpu_limit = config.get('CPULimits', str(p.pw_uid))
            
            if config.has_option('DiskLimits', str(p.pw_uid)):
                disk_limit = config.get('DiskLimits', str(p.pw_uid))
                disk_limit = int(float(disk_limit))
                disk_limit = caputils.integer_to_stringbytes(disk_limit)
            
            #...then print out the aggregated resource usage and corresponding system limits into table
            print(f"{p.pw_uid:<17}{p.pw_name:<17}{str(cpu_usage) + "%":<17}{caputils.integer_to_stringbytes(ram_usage):<17}{disk_usage if disk_usage else "N/A":<17}{cpu_limit + "%" if cpu_limit else "N/A":<17}{ram_limit if ram_limit else "N/A":<17}{disk_limit if disk_limit else "N/A":<17}")
            print("-------------------------------------------------------------------------------------------------------------------------------------------")

#Open up editor to edit configuration file--convenience command
def editor(app: str):
    config = configparser.ConfigParser()

    #Open up configuration file
    with open('/etc/setcap.ini', "r") as config_file:
        config.read_file(config_file)
    
    #If app argument supplied, save new preferred text editor executable
    if app:
        config.set("Editor", 'app', app)

        with open('/etc/setcap.ini', "w") as config_file:
            config.write(config_file)
    
    #Launch text editor with configuration file open
    os.system(f"sudo {config['Editor']['app']} /etc/setcap.ini")

#Commit addmod changes to the underlying techniques
def install():
    #Read from configuration file
    config = configparser.ConfigParser()

    with open('/etc/setcap.ini', "r") as config_file:
        config.read_file(config_file)
    
    #Get storage, CPU, and RAM limits from config for each user if it exists
    storage_limits = dict(config.items('DiskLimits'))

    for uid in storage_limits:
        subprocess.run(["sudo", "setquota", "-u", uid, str(int(float(storage_limits[uid]))), str(int(float(storage_limits[uid]))), "0", "0", "/"])
    
    cpu_limits = dict(config.items("CPULimits"))

    for uid in cpu_limits:
        converted_limit = int(cpu_limits[uid]) * 10000

        if not os.path.isdir(f'/sys/fs/cgroup/{uid}'):
            os.system(f"sudo mkdir /sys/fs/cgroup/{uid}")
        
        os.system(f"""sudo echo "{converted_limit} 1000000" | sudo tee /sys/fs/cgroup/{uid}/cpu.max""")

    
    ram_limits = dict(config.items("RAMLimits"))

    for uid in ram_limits:
        if not os.path.isdir(f'/sys/fs/cgroup/{uid}'):
            os.system(f"sudo mkdir /sys/fs/cgroup/{uid}")
        
        os.system(f"""sudo echo "{int(float(ram_limits[uid]))}" | sudo tee /sys/fs/cgroup/{uid}/memory.max""")
    
    #Open cgrules file
    cgconfig_file = open("/etc/cgrules.conf", "w")
    
    #Combine UIDs (one unique line in cgrules file per UID)
    cg_uids = list(ram_limits.keys()) + list(cpu_limits.keys())
    cg_uids = list(set(cg_uids))
    contents = ""
    
    #Write to cgrules file for each UID
    for uid in cg_uids:
        contents += f"{caputils.name_from_uid(int(uid))} cpu,ram /sys/fs/cgroup/{uid}\n"

    cgconfig_file.write(contents)

    cgconfig_file.close()

    #Run cgrulesengd to start/refresh it
    os.system(f"sudo cgrulesengd")